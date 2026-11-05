"""Kalshi trade-API auth + thin HTTP clients, shared by SharpLab, live-trader,
finance, and vigil — each had its own copy of the RSA-PSS signing scheme
(live-trader's was the original; SharpLab's `shared/kalshi_account.py` added
the PEM-newline repair and cursor pagination).

Only the transport is here: key loading, request signing, sync + async clients
with GET/cursor pagination, and balance parsing. App logic (PnL math, order
placement, orderbook parsing, market boards) stays in the app.

Signing per Kalshi's spec: RSA-PSS(SHA256, salt=digest length), or Ed25519 for
those keys, over `ts_ms + METHOD + path`, where path is everything after the host INCLUDING
`/trade-api/v2` and WITHOUT the query string.

Deps: `cryptography` + `httpx` (`pip install "djtoolkit[kalshi] @ git+..."`).
"""
from __future__ import annotations

import base64
import os
import time
from urllib.parse import urlsplit

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
PrivateKey = rsa.RSAPrivateKey | ed25519.Ed25519PrivateKey


class KalshiAuthError(httpx.HTTPStatusError):
    """Kalshi rejected the key (401/403). Subclasses HTTPStatusError so code that
    already catches httpx errors keeps working."""

    def __init__(self, message: str, *, request: httpx.Request | None = None,
                 response: httpx.Response | None = None) -> None:
        super().__init__(message, request=request, response=response)


# ---- keys + signing ---------------------------------------------------------

def load_key(pem: str | bytes) -> PrivateKey:
    """Parse a PEM private key. A paste that lost its newlines (Discord flattens
    them to spaces) is rebuilt into a valid PEM first."""
    if isinstance(pem, bytes):
        pem = pem.decode()
    pem = pem.strip()
    if "\n" not in pem and "-----" in pem:
        # "-----BEGIN RSA PRIVATE KEY----- MIIE... -----END RSA PRIVATE KEY-----"
        parts = pem.split("-----")
        if len(parts) >= 5:
            begin, body, end = parts[1], parts[2], parts[3]
            pem = f"-----{begin}-----\n" + "\n".join(body.split()) + f"\n-----{end}-----\n"
    key = serialization.load_pem_private_key(pem.encode(), password=None)
    if not isinstance(key, (rsa.RSAPrivateKey, ed25519.Ed25519PrivateKey)):
        raise ValueError("not an RSA or Ed25519 private key")
    return key


def load_key_file(path: str | os.PathLike) -> PrivateKey:
    with open(path, "rb") as f:
        return load_key(f.read())


def sign_path(base: str, path: str) -> str:
    """The path Kalshi signs: base's path prefix (/trade-api/v2) + api path, no query."""
    return urlsplit(base).path.rstrip("/") + path.split("?", 1)[0]


def sign_headers(key_id: str, key: PrivateKey, method: str, path: str,
                 ts_ms: int | None = None) -> dict[str, str]:
    """Auth headers for one request. `path` is the full URL path (incl. /trade-api/v2);
    any query string is stripped before signing."""
    ts = str(ts_ms if ts_ms is not None else int(time.time() * 1000))
    msg = f"{ts}{method.upper()}{path.split('?', 1)[0]}".encode()
    if isinstance(key, ed25519.Ed25519PrivateKey):
        sig = key.sign(msg)
    else:
        sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": key_id, "KALSHI-ACCESS-TIMESTAMP": ts,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode()}


# ---- balance parsing ---------------------------------------------------------
# /portfolio/balance returns integer cents (`balance`, `portfolio_value`) and/or
# fixed-point dollar strings (`balance_dollars`, ...), depending on API vintage.

def _num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _dollars(d: dict, field: str) -> float:
    if f"{field}_dollars" in d:
        return _num(d[f"{field}_dollars"])
    return _num(d.get(field)) / 100


def _cents(d: dict, field: str) -> int:
    if field in d:
        return int(_num(d[field]))
    return round(_num(d.get(f"{field}_dollars")) * 100)


def balance_dollars(bal: dict) -> float:
    """Cash balance in dollars."""
    return _dollars(bal, "balance")


def portfolio_value_dollars(bal: dict) -> float:
    """Mark value of open positions in dollars."""
    return _dollars(bal, "portfolio_value")


def account_value_cents(bal: dict) -> int:
    """Cash + open-position value, in integer cents."""
    return _cents(bal, "balance") + _cents(bal, "portfolio_value")


# ---- clients ---------------------------------------------------------------

def _page_path(path: str, limit: int, cursor: str) -> str:
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}limit={limit}" + (f"&cursor={cursor}" if cursor else "")


def _check(r: httpx.Response) -> None:
    if r.status_code in (401, 403):
        raise KalshiAuthError(f"Kalshi rejected the key ({r.status_code})", request=r.request, response=r)
    r.raise_for_status()


class _Base:
    def __init__(self, key_id: str, key: PrivateKey, base: str = KALSHI_BASE) -> None:
        self.key_id = key_id
        self.key = key
        self.base = base.rstrip("/")

    def headers(self, method: str, path: str) -> dict[str, str]:
        """`path` is relative to base (e.g. "/portfolio/balance?x=1")."""
        return {**sign_headers(self.key_id, self.key, method, sign_path(self.base, path)),
                "Content-Type": "application/json"}


class KalshiClient(_Base):
    """Sync client. `request`/`get` return parsed JSON; paths are relative to base."""

    def __init__(self, key_id: str, key: PrivateKey, base: str = KALSHI_BASE, *,
                 timeout: float = 10.0, http: httpx.Client | None = None) -> None:
        super().__init__(key_id, key, base)
        self.http = http or httpx.Client(timeout=timeout)

    @classmethod
    def from_key_file(cls, key_id: str, path: str | os.PathLike, base: str = KALSHI_BASE, **kw) -> "KalshiClient":
        return cls(key_id, load_key_file(path), base, **kw)

    def request(self, method: str, path: str, json=None) -> dict:
        r = self.http.request(method, self.base + path, headers=self.headers(method, path), json=json)
        _check(r)
        return r.json()

    def get(self, path: str) -> dict:
        return self.request("GET", path)

    def paginate(self, path: str, field: str, *, limit: int = 200, max_pages: int | None = 100) -> list[dict]:
        """Follow `cursor` until exhausted (or max_pages; None = no cap), concatenating `field`."""
        out, cur, n = [], "", 0
        while max_pages is None or n < max_pages:
            r = self.get(_page_path(path, limit, cur))
            out += r.get(field) or []
            cur, n = r.get("cursor"), n + 1
            if not cur:
                break
        return out

    def balance(self) -> dict:
        return self.get("/portfolio/balance")

    def close(self) -> None:
        self.http.close()


class AsyncKalshiClient(_Base):
    """Async twin of KalshiClient. Pass `http` to share one httpx.AsyncClient."""

    def __init__(self, key_id: str, key: PrivateKey, base: str = KALSHI_BASE, *,
                 timeout: float = 10.0, http: httpx.AsyncClient | None = None) -> None:
        super().__init__(key_id, key, base)
        self.http = http or httpx.AsyncClient(timeout=timeout)

    @classmethod
    def from_key_file(cls, key_id: str, path: str | os.PathLike, base: str = KALSHI_BASE, **kw) -> "AsyncKalshiClient":
        return cls(key_id, load_key_file(path), base, **kw)

    async def request(self, method: str, path: str, json=None) -> dict:
        r = await self.http.request(method, self.base + path, headers=self.headers(method, path), json=json)
        _check(r)
        return r.json()

    async def get(self, path: str) -> dict:
        return await self.request("GET", path)

    async def paginate(self, path: str, field: str, *, limit: int = 200,
                       max_pages: int | None = 100) -> list[dict]:
        out, cur, n = [], "", 0
        while max_pages is None or n < max_pages:
            r = await self.get(_page_path(path, limit, cur))
            out += r.get(field) or []
            cur, n = r.get("cursor"), n + 1
            if not cur:
                break
        return out

    async def balance(self) -> dict:
        return await self.get("/portfolio/balance")

    async def aclose(self) -> None:
        await self.http.aclose()

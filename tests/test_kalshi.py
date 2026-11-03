"""Behavior lock for djtoolkit.kalshi: signatures verify against Kalshi's signed
message, pagination follows cursors, balance parsing handles both field shapes."""
import asyncio
import base64
import json

import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from djtoolkit import kalshi as k

KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH)


def _verify(headers: dict, msg: bytes) -> None:
    KEY.public_key().verify(base64.b64decode(headers["KALSHI-ACCESS-SIGNATURE"]), msg, PSS, hashes.SHA256())


def _pem() -> str:
    return KEY.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                             serialization.NoEncryption()).decode()


def test_sign_headers_verify_and_strip_query():
    h = k.sign_headers("kid", KEY, "post", "/trade-api/v2/portfolio/orders?x=1", ts_ms=123)
    assert h["KALSHI-ACCESS-KEY"] == "kid" and h["KALSHI-ACCESS-TIMESTAMP"] == "123"
    _verify(h, b"123POST/trade-api/v2/portfolio/orders")


def test_load_key_flattened_pem_and_bytes(tmp_path):
    flat = " ".join(_pem().split("\n"))  # Discord paste that lost its newlines
    assert k.load_key(flat).private_numbers() == KEY.private_numbers()
    p = tmp_path / "k.pem"
    p.write_text(_pem())
    assert k.load_key_file(p).private_numbers() == KEY.private_numbers()


def _transport(seen: list):
    pages = {"": {"fills": [1, 2], "cursor": "c1"}, "c1": {"fills": [3], "cursor": ""}}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        if req.url.path.endswith("/denied"):
            return httpx.Response(401, json={})
        return httpx.Response(200, json=pages[req.url.params.get("cursor", "")])
    return httpx.MockTransport(handler)


def test_sync_paginate_signs_each_request():
    seen = []
    c = k.KalshiClient("kid", KEY, http=httpx.Client(transport=_transport(seen)))
    assert c.paginate("/portfolio/fills?min_ts=5", "fills") == [1, 2, 3]
    assert [r.url.params.get("cursor") for r in seen] == [None, "c1"]
    assert all(r.url.params["limit"] == "200" and r.url.params["min_ts"] == "5" for r in seen)
    r = seen[0]
    _verify(r.headers, f"{r.headers['KALSHI-ACCESS-TIMESTAMP']}GET/trade-api/v2/portfolio/fills".encode())
    assert c.paginate("/portfolio/fills", "fills", max_pages=1) == [1, 2]


def test_sync_post_body_and_auth_error():
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(401 if req.url.path.endswith("/denied") else 200, json={"ok": True})
    c = k.KalshiClient("kid", KEY, http=httpx.Client(transport=httpx.MockTransport(handler)))
    assert c.request("POST", "/portfolio/orders", json={"a": 1}) == {"ok": True}
    assert json.loads(seen[0].content) == {"a": 1}
    _verify(seen[0].headers, f"{seen[0].headers['KALSHI-ACCESS-TIMESTAMP']}POST/trade-api/v2/portfolio/orders".encode())
    with pytest.raises(k.KalshiAuthError):
        c.get("/denied")
    with pytest.raises(httpx.HTTPStatusError):  # still catchable as an httpx error
        c.get("/denied")


def test_async_paginate_and_auth_error():
    async def run():
        seen = []
        c = k.AsyncKalshiClient("kid", KEY, http=httpx.AsyncClient(transport=_transport(seen)))
        assert await c.paginate("/portfolio/fills", "fills") == [1, 2, 3]
        with pytest.raises(k.KalshiAuthError):
            await c.get("/denied")
        await c.aclose()
    asyncio.run(run())


def test_balance_parsing_both_shapes():
    cents = {"balance": 12345, "portfolio_value": 655}
    dollars = {"balance_dollars": "123.45", "portfolio_value_dollars": "6.55"}
    for bal in (cents, dollars):
        assert k.balance_dollars(bal) == pytest.approx(123.45)
        assert k.portfolio_value_dollars(bal) == pytest.approx(6.55)
        assert k.account_value_cents(bal) == 13000
    assert k.account_value_cents({}) == 0

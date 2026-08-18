"""Discord bot boilerplate shared across David's bots (sage, stavid, ...).

Ported from sage's cogs/__init__.py + services/error_reporting.py, stripped of
sage-specific DB/Sentinel-forwarding coupling. Three pieces:

- sanitize_error / command_error_handler: turn an exception into a safe
  user-facing message and reply to the interaction. No dependencies beyond
  discord.py (SQLAlchemy errors are recognized if sqlalchemy is installed).
- load_all_cogs: glob-load every cog module in a package, skip `_`-prefixed
  files, log (not raise) on a single cog's import failure.
- ErrorDeduper: fingerprint an exception by (type, file, function) so repeat
  occurrences bump a counter instead of re-alerting. Pure in-memory — wire
  its output into your own DB/webhook if you want persistence across restarts.
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import importlib
import logging
import pkgutil
import re
import time
from dataclasses import dataclass, field

import discord

try:
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:  # sqlalchemy is optional
    SQLAlchemyError = ()  # type: ignore[assignment]

log = logging.getLogger("djtoolkit.discord")

_PATH_RE = re.compile(r"(/opt|/home|/var|/usr|/tmp|/root|/etc)/\S*")
_TOKEN_RE = re.compile(r"(ghp_|sk-|xoxb-)[\w\-]+|[0-9a-fA-F]{40,}")
_TRACE_RE = re.compile(r'File ".*?", line \d+, in \w+')


def _strip_sensitive(text: str) -> str:
    text = _PATH_RE.sub("[path]", text)
    text = _TOKEN_RE.sub("[redacted]", text)
    text = _TRACE_RE.sub("[trace]", text)
    return text


def sanitize_error(exc: Exception) -> str:
    """Map an exception to a short, safe message. Raw exception text never
    reaches Discord — paths/tokens/tracebacks are the whole reason this exists."""
    if isinstance(exc, discord.NotFound):
        return "The requested resource was not found."
    if isinstance(exc, discord.Forbidden):
        return "I don't have permission to do that."
    if isinstance(exc, discord.HTTPException):
        return "Discord API error. Try again in a moment."
    if SQLAlchemyError and isinstance(exc, SQLAlchemyError):
        return "Database error. Try again."
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return "Operation timed out. Try again."
    return "Something went wrong. Check logs for details."


def command_error_handler(func):
    """Decorator for a slash-command callback: catches, logs, and replies
    with a sanitized message instead of leaking a raw traceback to Discord."""

    @functools.wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        try:
            return await func(self, interaction, *args, **kwargs)
        except Exception as exc:
            log.exception("Command %s failed", func.__name__)
            safe_msg = sanitize_error(exc)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(safe_msg, ephemeral=True)
                else:
                    await interaction.response.send_message(safe_msg, ephemeral=True)
            except Exception:
                pass

    return wrapper


async def load_all_cogs(bot, package_name: str) -> None:
    """Load every non-underscore-prefixed module in `package_name` as a cog
    extension. Logs and continues past a single cog's import failure instead
    of crashing bot startup over one bad file."""
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg or module_name.startswith("_"):
            continue
        ext = f"{package_name}.{module_name}"
        try:
            await bot.load_extension(ext)
        except Exception:
            log.exception("Failed to load cog %s", ext)


def compute_error_id(exception_type: str, file_path: str, function_name: str) -> str:
    """Stable 8-hex-char fingerprint for a (type, file, function) tuple."""
    seed = f"{exception_type}:{file_path}:{function_name}".encode()
    return hashlib.sha256(seed).hexdigest()[:8]


def _innermost_frame(exc: BaseException) -> tuple[str, str]:
    tb = exc.__traceback__
    if tb is None:
        return "?", "?"
    while tb.tb_next is not None:
        tb = tb.tb_next
    frame = tb.tb_frame
    return frame.f_code.co_filename, frame.f_code.co_name


@dataclass
class _Occurrence:
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0


@dataclass
class ErrorDeduper:
    """In-memory error fingerprint dedupe. Call `.see(exc)` from a top-level
    error handler; it returns (error_id, is_new, count) so you can alert once
    on the first occurrence and stay quiet on repeats.

    # ponytail: in-memory only, resets on restart. Wire `.see()`'s return
    # into your own DB table (mirroring sage's ErrorOccurrence model) if you
    # need persistence across restarts.
    """

    _seen: dict[str, _Occurrence] = field(default_factory=dict)

    def see(self, exc: BaseException) -> tuple[str, bool, int]:
        exc_type = type(exc).__name__
        file_path, function_name = _innermost_frame(exc)
        error_id = compute_error_id(exc_type, file_path, function_name)
        now = time.time()
        row = self._seen.get(error_id)
        if row is None:
            self._seen[error_id] = _Occurrence(count=1, first_seen=now, last_seen=now)
            return error_id, True, 1
        row.count += 1
        row.last_seen = now
        return error_id, False, row.count


def _demo() -> None:
    dd = ErrorDeduper()
    try:
        raise ValueError("boom")
    except ValueError as exc:
        id1, is_new1, count1 = dd.see(exc)
        assert is_new1 and count1 == 1
        assert sanitize_error(exc) == "Something went wrong. Check logs for details."
    try:
        raise ValueError("boom again")
    except ValueError as exc:
        id2, is_new2, count2 = dd.see(exc)
        # same (type, file, function) -> same fingerprint even though message differs
        assert id2 == id1 and not is_new2 and count2 == 2
    assert _strip_sensitive("/home/david/secret ghp_abc123token") == "[path] [redacted]"
    print("discord_kit self-check OK")


if __name__ == "__main__":
    _demo()

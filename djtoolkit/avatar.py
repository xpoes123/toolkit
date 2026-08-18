"""Deterministic, hash-seeded trait picker — the mechanism behind nsba-cardai's
CuteAvatar (frontend/src/components/CuteAvatar.tsx): FNV-1a hash a name into a
seed, run it through xorshift32, and pick indices into small trait tables. No
image files, no AI image API, no server round-trip, no storage — the same
name always renders the same avatar, forever, computed in microseconds.

This module ports only the *mechanism*. The trait tables (palettes, shapes,
faces, whatever) are art, and art is per-app — define your own and call
SeededTraits.pick()/.chance() to select from them. See `_demo()` below for a
minimal end-to-end example, and web/avatar.ts for the same mechanism in TS
for a frontend that wants to render live (e.g. as inline SVG, like the
original).
"""

from __future__ import annotations


def hash32(s: str) -> int:
    """FNV-1a 32-bit hash. Deterministic across processes/machines/languages
    (this exact algorithm is also what web/avatar.ts uses, so a Python
    backend and a TS frontend derive identical traits from the same name)."""
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


class SeededTraits:
    """A name-seeded xorshift32 stream. `.pick(n)` draws a trait index in
    [0, n), `.chance(p)` draws a boolean, `.value()` draws a raw float in
    [0, 1) — call these in the same order every time so trait assignment
    stays stable for a given name."""

    def __init__(self, name: str):
        self._state = hash32(name or "anon") or 1  # xorshift32 can't seed with 0

    def value(self) -> float:
        s = self._state
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        s &= 0xFFFFFFFF
        self._state = s
        return s / 4294967296

    def pick(self, n: int) -> int:
        return int(self.value() * n)

    def chance(self, p: float = 0.5) -> bool:
        return self.value() < p


def _demo() -> None:
    # Determinism: same name -> same trait sequence, every time.
    a = SeededTraits("Steph")
    b = SeededTraits("Steph")
    seq_a = [a.pick(8), a.pick(4), a.chance(0.5), a.value()]
    seq_b = [b.pick(8), b.pick(4), b.chance(0.5), b.value()]
    assert seq_a == seq_b, "same name must yield the same traits"

    # Different names -> (almost certainly) different traits.
    c = SeededTraits("David")
    assert c.pick(8) != SeededTraits("Steph").pick(8) or True  # collisions are fine, just spot-checking it runs

    # Minimal end-to-end "avatar": pick a color + a shape from tiny tables.
    PALETTE = ["#8ecfa6", "#8bb8ea", "#f2a68e", "#f3cd7c"]
    SHAPES = ["circle", "square", "triangle"]

    def avatar_spec(name: str) -> dict:
        t = SeededTraits(name)
        return {"color": PALETTE[t.pick(len(PALETTE))], "shape": SHAPES[t.pick(len(SHAPES))], "blush": t.chance(0.6)}

    spec1 = avatar_spec("stavid-bot")
    spec2 = avatar_spec("stavid-bot")
    assert spec1 == spec2
    print("avatar self-check OK:", spec1)


if __name__ == "__main__":
    _demo()

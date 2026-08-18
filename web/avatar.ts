// Deterministic, hash-seeded trait picker — same mechanism as djtoolkit/avatar.py
// (kept in lockstep: FNV-1a hash + xorshift32), so a Python backend and this
// frontend derive identical traits from the same name. Ported from
// nsba-cardai's CuteAvatar.tsx. Art (palettes/shapes/whatever) is yours —
// this is only the seed -> trait-index mechanism.

/** FNV-1a — stable across sessions, unlike Math.random seeding. */
export function hash32(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export class SeededTraits {
  private state: number;

  constructor(name: string) {
    this.state = hash32(name || "anon") || 1; // xorshift32 can't seed with 0
  }

  value(): number {
    let s = this.state;
    s ^= s << 13; s >>>= 0;
    s ^= s >>> 17;
    s ^= s << 5; s >>>= 0;
    this.state = s;
    return s / 4294967296;
  }

  pick(n: number): number {
    return Math.floor(this.value() * n);
  }

  chance(p = 0.5): boolean {
    return this.value() < p;
  }
}

// Self-check: `npx tsx avatar.ts` (or ts-node). Mirrors avatar.py's _demo().
function _demo() {
  const a = new SeededTraits("Steph");
  const b = new SeededTraits("Steph");
  const seqA = [a.pick(8), a.pick(4), a.chance(0.5), a.value()];
  const seqB = [b.pick(8), b.pick(4), b.chance(0.5), b.value()];
  console.assert(JSON.stringify(seqA) === JSON.stringify(seqB), "same name must yield the same traits");

  const PALETTE = ["#8ecfa6", "#8bb8ea", "#f2a68e", "#f3cd7c"];
  const SHAPES = ["circle", "square", "triangle"];
  function avatarSpec(name: string) {
    const t = new SeededTraits(name);
    return { color: PALETTE[t.pick(PALETTE.length)], shape: SHAPES[t.pick(SHAPES.length)], blush: t.chance(0.6) };
  }
  const s1 = JSON.stringify(avatarSpec("stavid-bot"));
  const s2 = JSON.stringify(avatarSpec("stavid-bot"));
  console.assert(s1 === s2, "avatarSpec must be deterministic");
  console.log("avatar.ts self-check OK:", s1);
}

if (typeof require !== "undefined" && require.main === module) {
  _demo();
}

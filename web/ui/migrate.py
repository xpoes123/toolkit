#!/usr/bin/env python3
"""Point a repo's html/css at the shared stylesheet. Usage: migrate.py [--apply] <dir>...
Replaces known palette hex with var(--token) and links https://share.djiang.xyz/ui/ui.css.
Own-variable declarations (--surface-2:#252a3a) become aliases (--surface-2:var(--surface)),
or are dropped when the name already is the shared token. Unknown colors are reported, not touched."""
import re, sys, pathlib, collections
LINK = '<link rel="stylesheet" href="https://share.djiang.xyz/ui/ui.css">'
M = {}
for tok, hexes in {
  "bg": "0a0d12 1a1b26 16161e 15161e 0c0f14 0b0e13 14131a 10131f 12141c", "surface-2": "1f2335 17161e",
  "surface": "141821 24283b 20232f 252a3a 1c1d29 22232f 1c1b25 22212b 232838", "line": "232936 1d2330 2f3549 292e42 2a2933 2b3145",
  "line-2": "414868 3b3a45 3b4363 3d4a7a", "text": "c0caf5 e8e3d8 e6e9ef", "text-2": "a9b1d6 a8a39a",
  "muted": "9aa3b2 565f89 787c99 7884b0 7c7971 6b6862 8087a8 7a83ad", "accent": "7aa2f7 d4a955 6a9bf0", "ok": "9ece6a 8fb573",
  "bad": "f7768e b54c4c e15c74", "warn": "e0af68 ff9e64", "info": "7dcfff 7fa7c4 73daca", "purple": "bb9af7 a58bb8 9d7cd8 8b7bc0"}.items():
    for h in hexes.split(): M[h] = tok
SHARED = set(M.values())
HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
DECL = re.compile(r"(--[\w-]+)(\s*:\s*)#([0-9a-fA-F]{6})\b(\s*;?)")
RAW = re.compile(r"(--[\w-]+)(\s*:\s*)#([0-9a-fA-F]{6})\b")
def conv(s, left):
    def decl(m):
        name, h = m.group(1)[2:], m.group(3).lower()
        if h not in M: left[h] += 1; return m.group(0)
        tok = M[h]
        if name == tok: return ""            # shared token already defines it
        return f"{m.group(1)}{m.group(2)}var(--{tok}){m.group(4)}"
    s = DECL.sub(decl, s)
    def use(m):
        h = m.group(1).lower()
        if h in M: return f"var(--{M[h]})"
        left[h] += 1; return m.group(0)
    return HEX.sub(use, s)
def main():
    apply = "--apply" in sys.argv; left = collections.Counter(); n = 0
    for root in [a for a in sys.argv[1:] if not a.startswith("--")]:
        for p in pathlib.Path(root).rglob("*"):
            if p.suffix not in (".html", ".css") or any(x in p.parts for x in ("node_modules", ".git", "dist", "_legacy", ".claude", ".venv", "archive")): continue
            if p.name in ("ui.css", "tokyo-night.css"): continue
            s = p.read_text(errors="replace"); o = s
            s = conv(s, left)
            if p.suffix == ".html" and "--no-link" not in sys.argv and "share.djiang.xyz/ui/ui.css" not in s:
                s = re.sub(r'<link[^>]*tokyo-night\.css[^>]*>', '', s)
                s, k = re.subn(r"(<head[^>]*>)", lambda m: m.group(1) + LINK, s, count=1)
                if not k: s = LINK + s
            if s != o:
                n += 1
                if apply: p.write_text(s)
    print(("applied" if apply else "would change"), n, "files; unmapped hex:", left.most_common(12))
main()

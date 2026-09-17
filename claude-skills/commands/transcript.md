Pull the transcript from a YouTube video URL ($ARGUMENTS) using yt-dlp.

Steps:
1. Run yt-dlp to download subtitles only (no video) into `/tmp/yt-transcript/`:
   ```
   mkdir -p /tmp/yt-transcript && cd /tmp/yt-transcript && \
   yt-dlp --write-auto-sub --write-sub --sub-lang en --skip-download \
          --sub-format vtt -o "%(id)s.%(ext)s" "<URL>"
   ```
   Prefers human-authored English subs; falls back to auto-generated.

2. Clean the resulting `<id>.en.vtt` into plain prose using this Python:
   ```python
   import re, pathlib, sys
   p = pathlib.Path(sys.argv[1])
   out, seen, last = [], set(), None
   for ln in p.read_text().splitlines():
       if not ln.strip(): continue
       if ln.startswith(("WEBVTT", "Kind:", "Language:")): continue
       if "-->" in ln or re.match(r"^\d+$", ln): continue
       txt = re.sub(r"<[^>]+>", "", ln).strip()
       if not txt or txt == last or txt in seen: continue
       seen.add(txt); last = txt
       out.append(txt)
   p.with_suffix(".txt").write_text(" ".join(out))
   ```
   The dedup logic matters — VTT files repeat lines as captions roll on screen.

3. Read the cleaned `.txt` file and report:
   - Word count
   - Path on disk (`/tmp/yt-transcript/<id>.txt`)
   - A 2–3 sentence summary of what the video is about

If the user follows up with "summarize" / "extract claims" / "compare to X",
work from the file already on disk — don't re-download.

If yt-dlp fails (private video, geoblock, no captions), say so plainly and
offer the manual fallback: user pastes transcript text from YouTube's
"Show transcript" panel.

## Install
Requires `yt-dlp` on PATH (`pacman -S yt-dlp` / `pip install yt-dlp` / `brew install yt-dlp`). Copy this file to `~/.claude/commands/transcript.md`. Invoke with `/transcript <youtube-url>`.

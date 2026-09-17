#!/usr/bin/env python3
"""Render an interactive proposal/blueprint from a spec JSON and publish it
to your own site. Usage:  python publish.py spec.json [--no-deploy]

Config (env vars, see SKILL.md):
  SITE_LOCAL_CLONE  - local git clone of your site's repo
  SITE_VPS_HOST     - ssh target for the VPS (host or ~/.ssh/config alias)
  SITE_VPS_PATH     - path to the site's working tree on the VPS
  SITE_DOMAIN       - public base URL, e.g. https://notes.yourdomain.com

spec.json:
{
  "title": "Finance Hub — v1 Spec",
  "subtitle": "Your call on each piece.",         # optional
  "project": "finance",                            # optional, default "misc"
  "mode": "proposal",                              # "proposal" | "blueprint"
  "blurb": "17 decisions — react & copy back",     # short chat line (echoed)
  "sections": [
    {"tag":"The core","title":"Per-category budgets","html":"<p>…</p>","suggest":false}
  ]
}
Prints the public URL and the blurb on success.
"""
import json, os, re, subprocess, sys
from datetime import date

SHARE = os.path.expanduser(os.environ.get("SITE_LOCAL_CLONE", "~/code/your-site-repo"))
VPS = os.environ.get("SITE_VPS_HOST", "user@your-vps-host")
VPS_PATH = os.environ.get("SITE_VPS_PATH", "/opt/your-site")
DOMAIN = os.environ.get("SITE_DOMAIN", "https://notes.yourdomain.com")
HERE = os.path.dirname(os.path.abspath(__file__))


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower().strip())
    return re.sub(r"[\s_-]+", "-", s)[:60].strip("-")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    deploy = "--no-deploy" not in sys.argv
    if not args:
        sys.exit("usage: python publish.py spec.json [--no-deploy]")
    spec = json.load(open(args[0]))

    title = spec["title"]
    project = spec.get("project", "misc")
    mode = spec.get("mode", "proposal")
    sections = spec["sections"]
    today = date.today().strftime("%Y-%m-%d")
    slug = f"{today}-{slugify(title)}"
    rel = f"{project}/{slug}.html"
    out = os.path.join(SHARE, rel)
    url = f"{DOMAIN}/{rel}"

    meta = {"title": title, "subtitle": spec.get("subtitle", ""),
            "mode": mode, "docKey": slug}

    tpl = open(os.path.join(HERE, "template.html")).read()
    html = (tpl.replace("__DOCTITLE__", esc(title))
               .replace("/*__META__*/{}", json.dumps(meta))
               .replace("/*__SECTIONS__*/[]", json.dumps(sections)))

    if deploy:
        run(["git", "-C", SHARE, "pull", "--ff-only"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)

    # Optional: register the page in a manifest-style page registry, if your
    # site has one (see the share-publish template). Skipped for plain
    # static sites.
    try:
        sys.path.insert(0, SHARE)
        from app import manifest
        data = manifest.load()
        data["projects"].setdefault(project, {"label": project.title(),
                                               "section": "Personal",
                                               "default_visibility": "unlisted"})
        manifest.upsert_page(data, {"file": rel, "project": project, "date": today,
                                    "title": title, "tag": "hub" if mode == "blueprint" else "brief",
                                    "visibility": "unlisted", "password": None, "redirect_from": []})
        manifest.save(data)
    except ImportError:
        pass

    if deploy:
        run(["git", "-C", SHARE, "add", "-A"])
        run(["git", "-C", SHARE, "commit", "-m", f"share: {project} — {title}"])
        run(["git", "-C", SHARE, "push"])
        run(["ssh", "-o", "ConnectTimeout=12", VPS, f"cd {VPS_PATH} && git pull --ff-only"])

    print("URL:", url)
    print("BLURB:", spec.get("blurb", ""))
    print("MODE:", mode, "| sections:", len(sections), "| deployed:", deploy)


if __name__ == "__main__":
    main()

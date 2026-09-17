VPS operations — SSH, deploy, logs, status, and file transfers for your own VPS.

**Template — this is a reusable pattern for the Hetzner/DigitalOcean/Linode-style
"one box, Caddy + systemd, several small services" setup. Fill in your own
values before use, either by editing this file or just telling Claude these
facts once at the start of a session.**

## Config — edit before use

- **Host**: `user@your-vps-ip-or-hostname` (or an alias in `~/.ssh/config`, e.g. `Host vps`)
- **Domain**: `yourdomain.com` and subdomains
- **Reverse proxy**: this template assumes Caddy at `/etc/caddy/Caddyfile` (auto-HTTPS). Swap in nginx/traefik conventions if that's what you run.
- **Service manager**: systemd, services under `/opt/`

SSH access:
```bash
ssh user@your-vps-host "command"
scp localfile user@your-vps-host:/remote/path
```

## Running services

Keep your own table here (subdomain, port, systemd unit, path) — it's the
single most useful reference for a multi-service box. Example shape:

| Service | Subdomain | Port | Path |
|---------|-----------|------|------|
| api | api.yourdomain.com | 8001 | /opt/api |
| worker | — (background) | — | /opt/api |
| blog | blog.yourdomain.com | — (static, served by Caddy) | /opt/blog |

Flag any service where a restart has real consequences (real users mid-session,
a job that can't be safely interrupted) so Claude checks with you before
touching it.

## Common operations

### Check status of a service
```bash
ssh user@your-vps-host "systemctl status <service>.service --no-pager"
```

### Pull logs (last 50 lines)
```bash
ssh user@your-vps-host "journalctl -u <service>.service -n 50 --no-pager"
```

### Deploy a service (git-backed, standard pattern)
```bash
ssh user@your-vps-host "cd /opt/<service> && git pull origin main && venv/bin/pip install -e . && systemctl restart <service>"
```
Deploy by pulling from git, not by scp'ing loose files — keeps the VPS and
the repo from drifting apart.

### Deploy a static site (copy files)
```bash
scp -r ./dist/* user@your-vps-host:/opt/<sitename>/
```

### Add a new subdomain (Caddy)
```bash
ssh user@your-vps-host "cat >> /etc/caddy/Caddyfile" << 'EOF'
newsite.yourdomain.com {
    reverse_proxy 127.0.0.1:PORT
}
EOF
ssh user@your-vps-host "systemctl reload caddy"
```

### Quick health check
```bash
ssh user@your-vps-host "systemctl list-units --type=service --state=failed --no-pager; free -h; df -h /"
```

## Deploying a brand new service

1. Write the code locally, test it.
2. Create `/opt/<service>` on the VPS, set up a venv, copy files:
   ```bash
   ssh user@your-vps-host "mkdir -p /opt/<service>"
   scp -r ./* user@your-vps-host:/opt/<service>/
   ssh user@your-vps-host "cd /opt/<service> && python3 -m venv venv && venv/bin/pip install -r requirements.txt"
   ```
3. Write a `.env` file with secrets (and lock it down):
   ```bash
   ssh user@your-vps-host "echo 'KEY=value' > /opt/<service>/.env && chmod 600 /opt/<service>/.env"
   ```
4. Install and start the systemd service:
   ```bash
   scp <service>.service user@your-vps-host:/etc/systemd/system/
   ssh user@your-vps-host "systemctl daemon-reload && systemctl enable --now <service>"
   ```
5. Add a Caddy block and reload (see above).

## Notes
- Prefer key-only SSH (`PermitRootLogin prohibit-password`, `PasswordAuthentication no`) and `fail2ban` jailing sshd; periodically diff `ufw`/firewall allow-rules against what's actually listening (`ss -ltn`) and remove stale rules.
- `.env` files should be `chmod 600` — `find /opt -maxdepth 2 -name '.env' -perm /044` is a quick way to catch ones that aren't.
- If you run a watchdog/auto-restart script for crashed services, tell Claude its name so it doesn't get killed by accident during troubleshooting.
- Never restart a service that's mid-transaction for a real user (payments, live sessions, in-flight jobs) without checking timing first — keep an explicit do-not-disturb list for those.

## Install
No dependencies beyond SSH access to your own box. Copy this file to `~/.claude/commands/vps-ops.md`, fill in the Config section (or just tell Claude the values), and invoke with `/vps-ops <what you want to do>`.

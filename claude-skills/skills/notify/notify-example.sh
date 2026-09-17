#!/usr/bin/env bash
# notify TITLE [BODY] [LEVEL=info|warn|crit] — post a message to a Discord
# channel via an incoming webhook. Minimal reference implementation for the
# `notify` skill — swap this out for Slack/ntfy/your own bot if you prefer.
#
# Setup: Discord channel -> Settings -> Integrations -> Webhooks -> New
# Webhook -> copy URL -> export DISCORD_WEBHOOK_URL="that url"
set -euo pipefail

: "${DISCORD_WEBHOOK_URL:?set DISCORD_WEBHOOK_URL to your Discord webhook URL first}"
TITLE=${1:?usage: notify TITLE [BODY] [LEVEL]}
BODY=${2:-}
LEVEL=${3:-info}

case "$LEVEL" in
  crit) COLOR=15158332 ;;   # red
  warn) COLOR=15105570 ;;   # orange
  *)    COLOR=3066993  ;;   # green
esac

PAYLOAD=$(jq -n --arg t "$TITLE" --arg b "$BODY" --argjson c "$COLOR" \
  '{embeds: [{title: $t, description: $b, color: $c}]}')

curl -sfS -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  --data-binary "$PAYLOAD" >/dev/null \
  && echo "notified" || { echo "notify FAILED" >&2; exit 1; }

#!/usr/bin/env bash
set -euo pipefail

IP=""
if command -v ip >/dev/null 2>&1; then
    IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") { print $(i + 1); exit }}')" || true
fi

if [[ -z "${IP}" ]] && hostname -I >/dev/null 2>&1; then
    IP="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
fi

if [[ -z "${IP}" ]]; then
    echo "${0##*/}: could not detect LAN IPv4 — set BROKER_HOST on the ESP" >&2
    exit 1
fi

exec avahi-publish-address --verbose mqtt "${IP}"

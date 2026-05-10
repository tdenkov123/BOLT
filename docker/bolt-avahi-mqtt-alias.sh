#!/usr/bin/env bash
set -euo pipefail

_pick_lan_ip() {
    if ! command -v ip >/dev/null 2>&1; then
        return 1
    fi
    ip -4 route show scope link 2>/dev/null | awk '
    {
        src = ""; dev = ""
        for (i = 1; i <= NF; i++) {
            if ($i == "src")  src = $(i+1)
            if ($i == "dev")  dev = $(i+1)
        }
        if (src == "" || dev == "") next
        # skip loopback, Docker bridges, virtual ethernet, libvirt bridges
        if (dev ~ /^(lo|docker[0-9]|br-[0-9a-f]|veth[a-z0-9]|virbr[0-9])/) next
        # skip Docker-range IPs: 172.16-31.x.x, 10.0.0.x
        n = split(src, a, ".")
        if (a[1] == 172 && a[2]+0 >= 16 && a[2]+0 <= 31) next
        if (a[1] == 10  && a[2]+0 == 0 && a[3]+0 == 0) next
        print src; exit
    }'
}

IP="$(_pick_lan_ip || true)"

# Fallback: take first non-loopback, non-Docker IP from hostname -I
if [[ -z "${IP}" ]] && hostname -I >/dev/null 2>&1; then
    for candidate in $(hostname -I 2>/dev/null); do
        IFS='.' read -r a b c d <<< "$candidate"
        # skip Docker/virtual ranges
        [[ "$a" == "127" ]] && continue
        [[ "$a" == "172" && "$b" -ge 16 && "$b" -le 31 ]] && continue
        IP="$candidate"
        break
    done
fi

if [[ -z "${IP}" ]]; then
    echo "${0##*/}: could not detect LAN IPv4 (Docker bridge excluded) — set BROKER_HOST manually on the ESP" >&2
    exit 1
fi

echo "${0##*/}: advertising mqtt.local → ${IP}"
exec avahi-publish-address --verbose mqtt "${IP}"

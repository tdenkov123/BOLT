import socket
import time

from config import (
    BROKER_MDNS_LOOKUP_ENABLED,
    BROKER_MDNS_NAME,
    BROKER_DISCOVERY_TIMEOUT_MS,
    BROKER_DISCOVERY_RETRIES,
    BROKER_EXTRA_HOSTS_TO_TRY,
    BROKER_HOST,
    BROKER_PORT,
)


def _looks_like_ipv4(s):
    parts = str(s).split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def _resolve_host_port(hostname, port):
    try:
        ais = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        if ais:
            sa = ais[0][-1]
            return sa[0], int(sa[1])
    except OSError:
        pass
    return None


def _mqtt_tcp_probe(ip, port, timeout_s):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(timeout_s)
            s.connect((ip, port))
            return True
        finally:
            s.close()
    except OSError:
        return False


def _discovery_candidates():
    names = []

    raw = (BROKER_MDNS_NAME or "").strip()
    if raw and not _looks_like_ipv4(raw):
        if raw.endswith(".local"):
            names.append(raw)
        else:
            names.append(raw + ".local")

    for extra in BROKER_EXTRA_HOSTS_TO_TRY:
        e = (extra or "").strip()
        if e and e not in names:
            names.append(e)

    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def discover_broker():
    try:
        return _discover_broker_inner()
    except Exception as e:
        print("[mDNS] discovery fatal error:", e, "— using fallback broker")
        return str(BROKER_HOST), int(BROKER_PORT)


def _discover_broker_inner():
    _quick_ip_probe_s = 0.35
    hb = str(BROKER_HOST)
    if _looks_like_ipv4(hb) and _mqtt_tcp_probe(hb, int(BROKER_PORT), _quick_ip_probe_s):
        print("[broker]", hb + ":" + str(int(BROKER_PORT)), "reachable — skip mDNS getaddrinfo")
        return hb, int(BROKER_PORT)

    if not BROKER_MDNS_LOOKUP_ENABLED:
        print("[broker] mDNS lookup disabled — using", BROKER_HOST, BROKER_PORT)
        return str(BROKER_HOST), int(BROKER_PORT)

    candidates = _discovery_candidates()

    probe_timeout = min(max(300, int(BROKER_DISCOVERY_TIMEOUT_MS)) / 1000.0, 2.5)
    deadline_ms = min(15000, 3000 + 2000 * int(BROKER_DISCOVERY_RETRIES))

    def _over_deadline(start):
        try:
            return time.ticks_diff(time.ticks_ms(), start) > deadline_ms
        except Exception:
            return False

    t_start = time.ticks_ms()

    if not candidates:
        print("[broker] No mDNS hostname(s) configured — using fallback ", BROKER_HOST)
        if _looks_like_ipv4(str(BROKER_HOST)) and _mqtt_tcp_probe(
            str(BROKER_HOST), int(BROKER_PORT), probe_timeout
        ):
            return str(BROKER_HOST), int(BROKER_PORT)
        return str(BROKER_HOST), int(BROKER_PORT)

    for attempt in range(1, int(BROKER_DISCOVERY_RETRIES) + 1):
        if _over_deadline(t_start):
            print("[broker] Discovery time budget exceeded — fallback", BROKER_HOST, BROKER_PORT)
            return str(BROKER_HOST), int(BROKER_PORT)
        print(
            "[broker] Resolve attempt",
            attempt,
            "/",
            int(BROKER_DISCOVERY_RETRIES),
            "candidates=",
            candidates or "(none)",
        )

        for name in candidates:
            ep = _resolve_host_port(name, BROKER_PORT)
            if not ep:
                continue
            ip, port = ep
            print("[broker] Resolved", name, "->", ip, ":", port)

            if _mqtt_tcp_probe(ip, port, probe_timeout):
                print("[broker] TCP probe OK, using broker", ip, port)
                return ip, port
            print("[broker] TCP probe failed for", ip, ":", port)

        if attempt < int(BROKER_DISCOVERY_RETRIES):
            time.sleep_ms(400)

    if _looks_like_ipv4(str(BROKER_HOST)):
        if _mqtt_tcp_probe(str(BROKER_HOST), int(BROKER_PORT), probe_timeout):
            print("[broker] Using fallback IP", BROKER_HOST, BROKER_PORT)
            return str(BROKER_HOST), int(BROKER_PORT)

    print(
        "[broker] Discovery failed — using configured",
        BROKER_HOST,
        BROKER_PORT,
        "(no TCP probe or probe failed)",
    )
    return str(BROKER_HOST), int(BROKER_PORT)

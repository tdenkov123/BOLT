import gc

gc.collect()
print("[mp] gc.mem_free", getattr(gc, "mem_free", lambda: "n/a")())

try:
    import network

    wlan = network.WLAN(network.STA_IF)
    print("[mp] Wi-Fi active=", wlan.active(), " connected=", wlan.isconnected())
    if wlan.isconnected():
        print("[mp] ifconfig", wlan.ifconfig())
except Exception as e:
    print("[mp] network check failed:", e)

try:
    import socket
    from config import BROKER_HOST, BROKER_PORT

    ai = socket.getaddrinfo(
        str(BROKER_HOST), int(BROKER_PORT), socket.AF_INET, socket.SOCK_STREAM
    )
    sa = ai[0][-1]
    print("[mp] config broker resolve ->", sa[0], sa[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect(sa[:2])
        print("[mp] TCP connect to config broker OK")
    finally:
        s.close()
except Exception as e:
    print("[mp] config broker TCP:", e)

try:
    import bolt_net

    bolt_net.init()
    bolt_net.await_discovery()
    print(
        "[mp] bolt_net RESOLVED ->",
        bolt_net.RESOLVED_BROKER_HOST,
        bolt_net.RESOLVED_BROKER_PORT,
    )
except Exception as e:
    print("[mp] bolt_net (import/init):", e)

print("[mp] done")

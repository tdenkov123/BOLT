import signal
import threading

from core.FunctionBlockLoader import FunctionBlockLoader
from core.BaseDevice import BaseDevice
from core.BaseResource import BaseResource


def main() -> None:
    loader = FunctionBlockLoader()
    start_class = loader.loadFBList(["core.FBs.START"])["START"]
    fb_classes = loader.loadFBList(["core.FBs.ADD_2", "core.FBs.PRINT_CONSOLE"])

    dev = BaseDevice("dev1")
    res = BaseResource("res1")
    dev.add_resource(res)

    res.create_fb(start_class("START"))
    res.create_fb(fb_classes["ADD_2"]("ADD_2"))
    res.create_fb(fb_classes["PRINT_CONSOLE"]("PRINT_CONSOLE"))

    res.connect_data("ADD_2", "OUT", "ADD_2", "IN2")
    res.connect_data("ADD_2", "OUT", "PRINT_CONSOLE", "IN")

    res.connect_event("START", "START", "ADD_2", "REQ")
    res.connect_event("ADD_2", "CNF", "ADD_2", "REQ")
    res.connect_event("ADD_2", "CNF", "PRINT_CONSOLE", "REQ")

    res.set_data("ADD_2", "IN1", 1)
    res.set_data("ADD_2", "IN2", 0)

    dev.start()

    dev.trigger_event("res1", "START", event="START")

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda s, f: stop.set())
    try:
        stop.wait()
    except KeyboardInterrupt:
        pass
    finally:
        dev.stop()


if __name__ == "__main__":
    main()

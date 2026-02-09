import asyncio

from core.FunctionBlockLoader import FunctionBlockLoader
from core.BaseDevice import BaseDevice
from core.BaseResource import BaseResource


async def main() -> None:
    loader = FunctionBlockLoader()
    start_class = loader.loadFBList(["core.FBs.START"])["START"]
    fb_classes = loader.loadFBList(["core.FBs.ADD_2", "core.FBs.PRINT_CONSOLE"])

    dev = BaseDevice("dev1")
    res = BaseResource("res1")
    dev.add_resource(res)

    res.add_fb(start_class("START"))
    res.add_fb(fb_classes["ADD_2"]("ADD_2"))
    res.add_fb(fb_classes["PRINT_CONSOLE"]("PRINT_CONSOLE"))

    res.connect_data("ADD_2", "OUT", "ADD_2", "IN2")
    res.connect_data("ADD_2", "OUT", "PRINT_CONSOLE", "IN")

    res.connect_event("START", "START", "ADD_2", "REQ")
    res.connect_event("ADD_2", "CNF", "ADD_2", "REQ")
    res.connect_event("ADD_2", "CNF", "PRINT_CONSOLE", "REQ")

    res.set_data("ADD_2", "IN1", 1)
    res.set_data("ADD_2", "IN2", 0)

    await dev.start()

    await dev.trigger_event("res1", "START") # to kickstart the chain

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await dev.stop()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from core.FunctionBlockLoader import FunctionBlockLoader
from core.device.BaseDevice import BaseDevice
from core.resource.BaseResource import BaseResource


async def main() -> None:
    loader = FunctionBlockLoader()
    fb_classes = loader.loadFBList(["core.FBs.ADD_2", "core.FBs.PRINT_CONSOLE"])

    dev = BaseDevice("dev1")
    res = BaseResource("res1")
    dev.add_resource(res)

    res.add_fb(fb_classes["ADD_2"]("ADD_2"))
    res.add_fb(fb_classes["PRINT_CONSOLE"]("PRINT_CONSOLE"))

    res.connect_data_push("ADD_2", "CNF", "OUT", "ADD_2", "IN2")
    res.connect_data_push("ADD_2", "CNF", "OUT", "PRINT_CONSOLE", "IN")

    res.connect_event("ADD_2", "CNF", "ADD_2", "REQ")
    res.connect_event("ADD_2", "CNF", "PRINT_CONSOLE", "REQ")

    res.set_data("ADD_2", "IN1", 1)
    res.set_data("ADD_2", "IN2", 0)

    while True:
        await dev.trigger_event("res1", "ADD_2") # to kickstart the chain, START block later
        await dev.run_event_cycle()


if __name__ == "__main__":
    asyncio.run(main())

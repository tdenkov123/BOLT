import asyncio

from core.FunctionBlockLoader import FunctionBlockLoader
from core.device.BaseDevice import BaseDevice
from core.resource.BaseResource import BaseResource


async def main() -> None:
    loader = FunctionBlockLoader()
    fb_classes = loader.loadFBList(["core.FBs.ADD_2"])

    dev = BaseDevice("dev1")
    res = BaseResource("res1")
    dev.add_resource(res)

    adder = fb_classes["ADD_2"]("adder")
    res.add_fb(adder)

    current = 0
    while True:
        current = adder.execute(current, 1)
        print(f"adder result: {current}")


if __name__ == "__main__":
    asyncio.run(main())
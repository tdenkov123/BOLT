import asyncio

from core.FunctionBlockLoader import FunctionBlockLoader


async def main() -> None:
    loader = FunctionBlockLoader()
    fb_classes = loader.loadFBList(["core.FBs.INT2INT", "core.FBs.ADD_2"])

    example_fb = fb_classes["INT2INT"]("ExampleFB")
    result = example_fb.execute(5)
    print(f"INT2INT execute result: {result}")

    a = fb_classes["INT2INT"]("FB1")
    b = fb_classes["ADD_2"]("FB2")

if __name__ == "__main__":
    asyncio.run(main())
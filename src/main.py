import asyncio

from core.FBs.FBootLoader import FBootLoader


async def main() -> None:
    loader = FBootLoader()
    loader.getFBList(["INT2INT"])  # supply only the blocks you need
    fb_classes = loader.loadFBList()

    example_fb = fb_classes["INT2INT"]("ExampleFB")
    result = example_fb.execute(5)
    print(f"INT2INT execute result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
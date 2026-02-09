from core.BaseFb import BaseFB

class START(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, event: str):
        return {}, ["START"]

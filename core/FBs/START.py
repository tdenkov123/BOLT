from core.BaseFunctionBlock import BaseFunctionBlock

class START(BaseFunctionBlock):
    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, event: str):
        return {}, ["START"]

from core.BaseFb import BaseFB

class PRINT_CONSOLE(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, event: str):
        if event == "REQ":
            val = self._inputs.get("IN")
            print(val)
            self._outputs = {}
            return self._outputs, ["CNF"]
        return {}, []

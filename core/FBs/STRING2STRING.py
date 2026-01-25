from core.BaseFb import BaseFB

class STR2STR(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, event: str):
        if event == "REQ":
            val = self._inputs.get("IN")
            self._outputs = {"OUT": str(val)}
            return self._outputs, ["CNF"]
        return {}, []

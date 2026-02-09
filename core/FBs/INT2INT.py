from core.BaseFunctionBlock import BaseFunctionBlock

class INT2INT(BaseFunctionBlock):
    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, event: str):
        if event == "REQ":
            val = self._inputs.get("IN")
            try:
                out_val = int(val) if val is not None else 0
            except:
                out_val = 0
            self._outputs = {"OUT": out_val}
            return self._outputs, ["CNF"]
        return {}, []

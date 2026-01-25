from core.BaseFb import BaseFB

class PRINT_CONSOLE(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self):
        val = self._inputs.get("IN")
        print(val)
        self._outputs = {"OUT": val}
        return self._outputs

    def getEventOutputs(self):
        return ["CNF"]

    def getEventInputs(self):
        return ["REQ"]

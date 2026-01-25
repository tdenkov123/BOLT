from core.BaseFb import BaseFB

class STR2STR(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self):
        val = self._inputs.get("IN")
        self._outputs = {"OUT": str(val)}
        return self._outputs

    def getEventOutputs(self):
        return ["CNF"]

    def getEventInputs(self):
        return ["REQ"]

from core.BaseFb import BaseFB

class INT2INT(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self):
        val = self._inputs.get("IN")
        try:
            out_val = int(val) if val is not None else 0
        except:
            out_val = 0
        self._outputs = {"OUT": out_val}
        return self._outputs

    def getEventOutputs(self):
        return ["CNF"]

    def getEventInputs(self):
        return ["REQ"]

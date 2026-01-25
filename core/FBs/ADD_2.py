from core.BaseFb import BaseFB

class ADD_2(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self):
        a = self._inputs.get("IN1", 0)
        b = self._inputs.get("IN2", 0)
        try:
            out_val = a + b
        except:
            out_val = 0
        self._outputs = {"OUT": out_val}
        return self._outputs

    def getEventOutputs(self):
        return ["CNF"]

    def getEventInputs(self):
        return ["REQ"]

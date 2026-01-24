from core.BaseFb import BaseFB

class STR2STR(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, inputValue: str) -> int:
        return str(inputValue)

    def getEventOutputs(self):
        return ["CNF"]
    def getEventInputs(self):
        return ["REQ"]

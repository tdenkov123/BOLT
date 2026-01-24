from core.BaseFb import BaseFB

class ADD_2(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, inputValue1: int, inputValue2: int) -> int:
        return inputValue1 + inputValue2

    def getEventOutputs(self):
        return ["CNF"]
    def getEventInputs(self):
        return ["REQ"]

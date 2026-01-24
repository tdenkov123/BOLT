from core.BaseFb import BaseFB

class INT2INT(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, inputValue: str) -> int:
        return int(inputValue)

    def getEventOutputs(self):
        return ["CNF"]
    def getEventInputs(self):
        return ["REQ"]

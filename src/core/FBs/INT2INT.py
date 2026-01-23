from core.BaseFb import BaseFB

class INT2INT(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, input_value: int) -> int:
        return int(input_value)

    def getEventOutputs(self):
        return ["CNF"]
    def getEventInputs(self):
        return ["REQ"]
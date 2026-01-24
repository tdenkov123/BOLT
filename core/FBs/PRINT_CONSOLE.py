from core.BaseFb import BaseFB

class PRINT_CONSOLE(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)

    def execute(self, inputValue: str) -> None:
        print(inputValue)

    def getEventOutputs(self):
        return ["CNF"]
    def getEventInputs(self):
        return ["REQ"]

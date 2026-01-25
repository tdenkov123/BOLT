class BaseFB:
    def __init__(self, name: str):
        self.name = name
        self._inputs = {}
        self._outputs = {}

    def set_input(self, name: str, value):
        self._inputs[name] = value

    def get_output(self, name: str):
        return self._outputs.get(name)

    def execute(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def getEventOutputs(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def getEventInputs(self):
        raise NotImplementedError("Subclasses should implement this method.")
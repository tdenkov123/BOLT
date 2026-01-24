class BaseFB:
    def __init__(self, name: str):
        self.name = name
        

    def execute(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
    def getEventOutputs(self):
        raise NotImplementedError("Subclasses should implement this method.")
    
    def getEventInputs(self):
        raise NotImplementedError("Subclasses should implement this method.")
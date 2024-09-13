from abc import ABC, abstractmethod

class Processor(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class LaneProcessor(Processor):
    def execute(self, data):
        print("LaneProcessor")

class ObstacleProcessor(Processor):
    def execute(self, data):
        print("ObstacleProcessor")
    
        

    


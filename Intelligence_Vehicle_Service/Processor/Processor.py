from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject

class Processor(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class ProcessorMeta(type(QObject), type(Processor)):
    pass


    
        

    


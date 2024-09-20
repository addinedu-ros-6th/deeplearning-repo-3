import sys
import os
from typing import Generic, Type, TypeVar
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor
from Intelligence_Vehicle_Service.DataHandler.DataHandler import DataHandler
from abc import ABC, abstractmethod

T = TypeVar('T')

class Factory(ABC, Generic[T]):
    def __init__(self):
        self.items = {}

    def register(self, key: str, item: Type[T]):
        self.items[key] = item

    def get(self, key: str) -> T:
        item = self.items.get(key)
        if not item:
            raise ValueError(f"Invalid item key: {key}")
        return item

class ProcessorFactory(Factory[Processor]):
    pass

class DataHandlerFactory(Factory[DataHandler]):
    pass

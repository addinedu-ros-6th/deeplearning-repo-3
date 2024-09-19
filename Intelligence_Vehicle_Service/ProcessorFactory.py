import sys
import os
from typing import Type
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor

class ProcessorFactory:
    def __init__(self) -> None:
        self.processors = {}

    def register_processor(self, key, processor: Type[Processor]):
        self.processors[key] = processor

    def get_processor(self, name) -> Processor:
        processor = self.processors.get(name)
        if not processor:
            raise ValueError(f"Invalid processor name: {name}")
        return processor
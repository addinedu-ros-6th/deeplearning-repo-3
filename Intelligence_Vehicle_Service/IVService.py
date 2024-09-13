import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from typing import Any
from flask import Flask, request, jsonify
from Intelligence_Vehicle_Service.ProcessorFactory import *
from Intelligence_Vehicle_Service.Processor.Processor import *
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient

class IVService:

    def __init__(self) -> None:
        self.processor_factory = ProcessorFactory()
        self.processor_factory.register_processor("lane", LaneProcessor)
        self.processor_factory.register_processor("obstacle", ObstacleProcessor)

        
    def handle_receive_data(self, from_client, key, data):
        print('\033[91m'+"Received data: from_client=" +'\033[92m'+f"{from_client}, key={key}," +'\033[96m'+ f"data={data}", '\033[0m')
        if key is None:
            print(f"Warning: Received data with no key from {from_client}")
            return

        try:
            self.processor = self.processor_factory.get_processor(key)
            self.processor.execute(data)

        except ValueError as e:
            print(f"Error processing data: {e}")






    



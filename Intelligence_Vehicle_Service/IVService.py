import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from typing import Any, Dict, List
from flask import Flask, request, jsonify
from Intelligence_Vehicle_Service.ProcessorFactory import ProcessorFactory
from Intelligence_Vehicle_Service.Processor.LaneProcessor import LaneProcessor
from Intelligence_Vehicle_Service.Processor.ObstacleProcessor import ObstacleProcessor
from Intelligence_Vehicle_Service.Processor.GUIViewerProcessor import GUIViewerProcessor
from Intelligence_Vehicle_Service.Processor.GUIProcessor import GUIProcessor
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient

class IVService:

    def __init__(self) -> None:
        self.client : FlaskClient = None
        self.client_addresses = self.set_clinet_addresses()
        self.processor_factory = ProcessorFactory()

    def register_ai_processor(self):
        self.processor_factory.register_processor("lane", LaneProcessor())
        self.processor_factory.register_processor("obstacle", ObstacleProcessor())
            
    def register_gui_processor(self, window_class):
        gui_viewer_processor = GUIViewerProcessor()
        gui_viewer_processor.frontView.connect(window_class.update_front_view)
        gui_viewer_processor.laneView.connect(window_class.update_lane_view)
        self.processor_factory.register_processor("viewer", gui_viewer_processor)

        gui_processor = GUIProcessor()
        # gui_processor.speedfunc.connect(window_class)
        self.processor_factory.register_processor("gui", gui_processor)


    def set_client(self, client:FlaskClient):
        print("set_client")
        self.client = client

    def set_clinet_addresses(self):
        return {
            "Lane": 5001,
            "Obstacle": 5002,
            "DB": 5003,
            "Service": 5004,
            "GUI": 5005
        }

    def handle_receive_data(self, from_client, key, data):
        # print('\033[91m'+"Received data: from_client=" +'\033[92m'+f"{from_client}, key={key}," +'\033[96m'+ f"data={data}", '\033[0m')
        if key is None:
            print(f"경고: {from_client}로부터 키 없이 데이터를 받았습니다.")
            return

        try:
            processor = self.processor_factory.get_processor(key)
            processor.execute(data)

        except ValueError as e:
            print(f"Error processing data: {e}")

    def handle_receive_tcp_data(self, data, client_address):
        print(f"receive_tcp: 클라이언트 {client_address}로부터 {data} 데이터 수신")

        # 로봇에게 속도 값을 통신을 받으면
        # GUI 에게 속도를 전송하고
        # self.client.send_data(f"http://localhost:{self.client_addresses['GUI']}", "gui", {"data":{"type": "speed", "data":data}})

        # DB에 값을 저장하고
        # self.client.send_data(f"http://localhost:{self.client_addresses['DB']}", "db", {"data":{"type":"insert", "table":"DrivingLog","data":data}})

        






    



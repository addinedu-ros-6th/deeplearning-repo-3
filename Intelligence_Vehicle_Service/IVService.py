import sys
import os
import cv2

from Intelligence_Vehicle_Communicator.TCPServerNewVersion import TCPServerManager

current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from typing import Any, Dict, List
from flask import Flask, request, jsonify
from Intelligence_Vehicle_Service.Factory import ProcessorFactory, DataHandlerFactory
from Intelligence_Vehicle_Service.Processor.ReceiveImageProcessor import ReceiveImageProcessor
from Intelligence_Vehicle_Service.Processor.LaneProcessor import LaneProcessor
from Intelligence_Vehicle_Service.Processor.ObstacleProcessor import ObstacleProcessor
from Intelligence_Vehicle_Service.Processor.GUIViewerProcessor import GUIViewerProcessor
from Intelligence_Vehicle_Service.Processor.GUIProcessor import GUIProcessor
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager
from Intelligence_Vehicle_Service.DataHandler.DataHandler import *


class IVService:

    def __init__(self) -> None:
        self.client : FlaskClient = None
        self.client_addresses = self.set_clinet_addresses()
        self.processor_factory = ProcessorFactory()
        self.data_handler_factory = DataHandlerFactory()
    
    def start_tcp_server(self):
        HOST = 'localhost'
        PORT = 4001
        
        try:
            tcp_server_manager = TCPServerManager()
            tcp_server_manager.start_server(host= 'localhost', port=PORT, data_handler=self.handle_receive_tcp_data)
        except KeyboardInterrupt:
            print("사용자로부터 종료 요청을 받았습니다.")
            tcp_server_manager.stop_all_clients()
        finally:
            tcp_server_manager.stop_server()
            print("프로그램이 완전히 종료되었습니다.")
        
    
    def register_receive_image_processor(self, receive_handle):
        receiveImageProcessor = ReceiveImageProcessor()
        self.processor_factory.register("receive_image", receiveImageProcessor)


    def register_ai_processor(self):
        laneProcessor = LaneProcessor()
        laneProcessor.set_error_callback(self.handle_lane_error_update)
        self.processor_factory.register("lane", laneProcessor)

        obstacleProcessor = ObstacleProcessor()
        self.processor_factory.register("obstacle", obstacleProcessor)
           

    def register_gui_processor(self, window_class):
        gui_viewer_processor = GUIViewerProcessor()
        gui_viewer_processor.frontView.connect(window_class.update_front_view)
        gui_viewer_processor.laneView.connect(window_class.update_lane_view)
        self.processor_factory.register("viewer", gui_viewer_processor)

        gui_processor = GUIProcessor()
        # gui_processor.speedfunc.connect(window_class)
        self.processor_factory.register("gui", gui_processor)

    def register_tcp_receive_handle(self):
        self.data_handler_factory.register("obstacle", ObstacleImageHandler())
        self.data_handler_factory.register("lane", LaneImageHandler())
        self.data_handler_factory.register("speed", SpeedDataHandler())


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

    def handle_receive_http_data(self, from_client, key, data):
        # print('\033[91m'+"Received data: from_client=" +'\033[92m'+f"{from_client}, key={key}," +'\033[96m'+ f"data={data}", '\033[0m')
        if key is None:
            print(f"경고: {from_client}로부터 키 없이 데이터를 받았습니다.")
            return

        try:
            processor = self.processor_factory.get(key)
            processor.execute(data)

        except ValueError as e:
            print(f"Error processing data: {e}")
         
    def handle_receive_tcp_data(self, data_type, data, client_address):
        # print(f"receive_tcp: 클라이언트 {client_address}로부터 {data} 데이터 수신")
        # key = data['key']
        # data_type : 1-str, 2-image

        if data[0] is None:
            print(f"경고: {client_address}로부터 키 없이 데이터를 받았습니다.")
            return

        try:
            handler = self.data_handler_factory.get(data[0])
            handler.handle(data, client_address=client_address)

        except ValueError as e:
            print(f"Error processing data: {e}")

        # 로봇에게 이미지를 받으면
        # identifier, image_data = data
        # print(f"이미지: {type(image_data)}")

        # threading.Thread(target=display_image, args=(identifier, image_data)).start()
        # if identifier == 'IF':
        #     print("정면 카메라 이미지 수신")
        # elif identifier == 'IL':
        #     print("차선 카메라 이미지 수신")
        
    def handle_lane_error_update(self, error: float):
        print(f"Lane error updated: {error}")

        # Robot에게 에러값 전달하고 
        # self.tcp_error_client.send_message(str(error))

        # db 에게 에러값 전달하자.
        





    



import sys
import os
import cv2

from Intelligence_Vehicle_Communicator.TCPServerNewVersion import TCPServerManager
from Intelligence_Vehicle_Communicator.UDPClient import UDPClientManager
from Intelligence_Vehicle_Communicator.UDPServer import UDPServerManager

current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from typing import Any, Dict, List
from flask import Flask, request, jsonify
from Intelligence_Vehicle_Service.Factory import ProcessorFactory, DataHandlerFactory
from Intelligence_Vehicle_Service.Processor.LaneProcessor import LaneProcessor
from Intelligence_Vehicle_Service.Processor.ObstacleProcessor import ObstacleProcessor
from Intelligence_Vehicle_Service.Processor.GUIViewerProcessor import GUIViewerProcessor
from Intelligence_Vehicle_Service.Processor.GUIProcessor import GUIProcessor
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager
from Intelligence_Vehicle_Service.DataHandler.DataHandler import *
from Intelligence_Vehicle_Communicator.UDPConnection import UDPConnection

class SocketConfig:

    # SERVER_HOST = '192.168.0.22'
    # CLIENT_HOST = '192.168.0.11'

    SERVER_HOST = '192.168.26.136'
    CLIENT_HOST = '192.168.26.178'
    @classmethod
    def get_host(cls):
        return cls.HOST


class IVService:

    def __init__(self) -> None:
        self.http_client : FlaskClient = None
        self.client_addresses = self.set_clinet_addresses()
        self.processor_factory = ProcessorFactory()
        self.data_handler_factory = DataHandlerFactory()

    def start_socket_client(self, port=4001):
        print("start_socket_client")
        udp_client_manager = UDPClientManager()
        self.client_error = udp_client_manager.get_client("error", "str", host= SocketConfig.CLIENT_HOST, port=port)
        self.client_error.start()

    
    def start_socket_server(self, port=4001):
        
        try:
            udp_server_manager = UDPServerManager()
            udp_server_manager.start_server(host=SocketConfig.SERVER_HOST, port=port,data_handler=self.handle_receive_socket_data)
            
            # tcp_server_manager = TCPServerManager()
            # tcp_server_manager.start_server(host= host, port=port, data_handler=self.handle_receive_tcp_data)
        
            # client_manager = TCPClientManager()
            # self.tcp_client = client_manager.get_client("speed", 'str', host='192.168.0.1', port=4006)
            # self.tcp_client.start()
        
        except KeyboardInterrupt:
            print("사용자로부터 종료 요청을 받았습니다.")
            udp_server_manager.stop_server()
        

    def register_ai_processor(self):
        laneProcessor = LaneProcessor()
        laneProcessor.set_error_callback(self.receive_lane_error)
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


    def set_tcp_data_handler_callback(self, key, func_tuple):
        data_handle = self.data_handler_factory.get(key)
        data_handle.register_data_received_callback((func_tuple[0], func_tuple[1]))



    def set_client(self, client:FlaskClient):
        print("set_client")
        self.http_client = client

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
         

    def handle_receive_socket_data(self, data_type, data, client_address):
        if data_type == 2:  # 이미지 데이터
            identifier, image = data
            # print(f' ==> Line 112: \033[38;2;16;122;195m[image]\033[0m({type(image).__name__}) = \033[38;2;185;179;31m{image}\033[0m')
            # print(f' ==> Line 112: \033[38;2;52;183;82m[identifier]\033[0m({type(identifier).__name__}) = \033[38;2;228;53;84m{identifier}\033[0m')

            try:
                handler = self.data_handler_factory.get(identifier)
                handler.handle(data, client_address=client_address)

            except ValueError as e:
                print(f"Error processing data: {e}")



    def receive_lane_error(self, error: float):

        print(f' ==> Line 137: \033[38;2;33;220;13m[error]\033[0m({type(error).__name__}) = \033[38;2;84;176;68m{error}\033[0m')
        self.client_error.queue_data((str(error), "ER"))




    def send_data_http(self, key, data, send_client_id):
        print(f' ==> Line 145: \033[38;2;112;249;126m[key]\033[0m({type(key).__name__}) = \033[38;2;16;208;72m{key}\033[0m')
        self.http_client.send_data(f"http://localhost:{self.client_addresses[send_client_id]}", key, {"data":data})


        # client.send_data(f"http://localhost:{clients['Service']}", "obstacle", {"data":obstacle_data})
        # client.send_data(f"http://localhost:{clients['GUI']}", "viewer", {"data":{"type": "front", "image":encodeimage}})







    



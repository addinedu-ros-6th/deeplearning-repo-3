import sys
import os

import cv2
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../..')  # 상위 폴더로 이동
sys.path.append(relative_path)
import time
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from lane_detector import LaneDetector 
import base64


clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004,
    "GUI": 5005
}

if __name__ == "__main__":

    detector = LaneDetector(model_path='Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                                video_path='Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

    service = IVService()
    service.register_tcp_receive_handle()
    service.set_tcp_data_handler_callback("lane", (detector.start_lane_result, service.send_data_http))

    client = FlaskClient(client_id="Lane", port=clients["Lane"])
    service.set_client(client)
    client.set_callback(service.handle_receive_http_data)

    while True:
        # , clients["GUI"]
        if client.is_port_open(host='localhost', ports=[clients["Service"]]):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    service.start_tcp_server(host='192.168.0.22', port=4001)
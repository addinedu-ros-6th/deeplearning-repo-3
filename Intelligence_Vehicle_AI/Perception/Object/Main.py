import sys
import os
import cv2
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../..')  # 상위 폴더로 이동
sys.path.append(relative_path)

import time
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from ObstacleDetector import ObstacleDetector 
import random
import base64


clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004,
    "GUI": 5005
}

def encode_image(image):
    _, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

if __name__ == "__main__":
    service = IVService()
    client = FlaskClient(client_id="Obstacle", port=clients["Obstacle"])
    client.set_callback(service.handle_receive_data)

    while True:
        if client.is_port_open(host='localhost', ports= [clients["GUI"], clients["Service"]]):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    obstacle_detector = ObstacleDetector('Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt',
                                 'Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4')
    
    for results, image in obstacle_detector.get_results():
        obstacle_data = {
            "results": results[0].tojson() # results 변환
        }
        encodeimage = encode_image(image)

        client.send_data(f"http://localhost:{clients['Service']}", "obstacle", {"data":obstacle_data})
        client.send_data(f"http://localhost:{clients['GUI']}", "viewer", {"data":{"type": "obstacle", "image":encodeimage}})









    # obstacle_data = {
    #     "x1": random.uniform(-1.0, 1.0),
    #     "x2": random.uniform(0, 0.001),
    #     "x3": random.uniform(0, 0.001)
    # }
    # client.send_data(f"http://localhost:{clients['Service']}", "obstacle", {"data": obstacle_data})

    
    # # LaneDetector 초기화
    # lane_data = {
    #     "lane_position": 10,
    #     "lane_curvature": 0.001
    # }
    # client.send_data(f"http://localhost:{clients['Service']}", "lane", {"data": lane_data})
    # obstacle_detector = ObstacleDetector(model_path='Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt',
    #                              video_path='Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4')


    # 1. Json으로 만들기
    """
        lane_data = {
        "lane_position": random.uniform(-1.0, 1.0),
        "lane_curvature": random.uniform(0, 0.001)
    }
    """
    
    # 2. Service에 데이터 전송하기
    """
        client.send_data(f"http://localhost:{clients['Service']}", {"data": lane_data})
    """
    # 3. 터미널에서 실행
    # 아래의 경로에서 터미널에 실행하면 main.py 2개가 각각의 터미널에서 실행됨.
    ## (yolo) mr@mr:~/dev_ws/deeplearning-repo-3$ 
    """
gnome-terminal -- bash -c "python3 Intelligence_Vehicle_Service/Main.py; exec bash" & gnome-terminal -- bash -c "python3 Intelligence_Vehicle_AI/Perception/Object/main.py; exec bash"
    """

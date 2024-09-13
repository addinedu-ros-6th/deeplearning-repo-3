import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../..')  # 상위 폴더로 이동
sys.path.append(relative_path)

import time

from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from lane_detector import LaneDetector 



clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004
}

if __name__ == "__main__":
    service = IVService()
    client = FlaskClient(client_id="Lane", port=clients["Lane"])
    client.set_callback(service.handle_receive_data)

    while True:
        if client.is_port_open(host='localhost', port=clients["Service"]):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    # # LaneDetector 초기화
    # lane_data = {
    #     "lane_position": 10,
    #     "lane_curvature": 0.001
    # }
    # client.send_data(f"http://localhost:{clients['Service']}", "lane", {"data": lane_data})
    lane_detector = LaneDetector(model_path='Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                                 video_path='Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

    # 비디오 처리 및 결과 전송
    for error, stop_line_flag in lane_detector.process_video():
        lane_data = {
            "error": error,
            "stop_line_flag": stop_line_flag
        }
        client.send_data(f"http://localhost:{clients['Service']}", "lane", {"data": lane_data})



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
gnome-terminal -- bash -c "python3 Intelligence_Vehicle_Service/Main.py; exec bash" & gnome-terminal -- bash -c "python3 Intelligence_Vehicle_AI/Perception/Lane/Main.py; exec bash"
    """

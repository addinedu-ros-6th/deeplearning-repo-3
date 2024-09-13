import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient

clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004
}

if __name__ == "__main__":
    service = IVService()
    client = FlaskClient(client_id="Service", port= clients["Service"])
    client.set_callback(service.handle_receive_data)

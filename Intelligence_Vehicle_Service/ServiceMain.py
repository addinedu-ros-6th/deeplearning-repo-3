import sys
import os
import time

import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from Intelligence_Vehicle_Communicator.TCPServerNewVersion import TCPServerManager, TCPServer

# clients = {
#     "Lane": 5001,
#     "Obstacle": 5002,
#     "DB": 5003,
#     "Service": 5004,
#     "GUI": 5005
# }

if __name__ == "__main__":
    service = IVService()
    service.register_ai_processor()
    service.register_tcp_receive_handle()
    service.start_tcp_server()

    client = FlaskClient(client_id="Service", port=service.client_addresses["Service"])
    service.set_client(client)
    service.client.set_callback(service.handle_receive_http_data)

    wait_ports = []
    # wait_ports.append(service.client_addresses["GUI"])
    # wait_ports.append(service.client_addresses["DB"])

    while True:
        if service.client.is_port_open(host='localhost', ports=wait_ports):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    





import random
import socket
import sys
import os
import threading
import time

import cv2
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from Intelligence_Vehicle_Service.IVService import IVService, SocketConfig
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from Custom_print import custom_print

if __name__ == "__main__":
    service = IVService()
    service.register_ai_processor()
    service.register_socket_receive_handle()
    service.set_socket_data_handler_callback("speed", (service.send_data_http()))

    client = FlaskClient(client_id="Service", port=service.client_addresses["Service"])
    service.set_client(client)
    service.http_client.set_callback(service.handle_receive_http_data)

    wait_ports = []
    wait_ports.append(service.client_addresses["GUI"])

    while True:
        if service.http_client.is_port_open(host='localhost', ports=wait_ports):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    service.start_socket_client(port=4002)




    





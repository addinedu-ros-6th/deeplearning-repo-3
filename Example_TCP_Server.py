import os
import sys
import time
import numpy as np


current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager
from Intelligence_Vehicle_Communicator.TCPServerNewVersion import TCPServerManager
from Intelligence_Vehicle_Service.IVService import IVService

def get_image():
    return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)

def get_text():
    return "Hello"

HOST = 'localhost'
PORT = 4001

if __name__== "__main__":
    service = IVService()
    service.start_tcp_server()



        


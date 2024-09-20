import os
import sys
import threading
import time
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.UDPServer import UDPServerManager
from Intelligence_Vehicle_Service.IVService import IVService

def get_image():
    return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)

def get_text():
    return "Hello"

HOST = 'localhost'
PORT = 4001

class UDPIVService(IVService):
    def start_udp_server(self):
        self.server_manager = UDPServerManager()
        self.server_manager.start_server(host=HOST, port=PORT, data_handler=self.udp_data_handler)

    def udp_data_handler(self, data_type, data, client_address):
        if data_type == 2:  # 이미지 데이터
            identifier, image_data = data
            print(f"UDP 이미지 수신: {identifier}, shape: {image_data.shape}")
            if identifier == 'lane':
                # 여기에서 차선 검출 로직을 실행할 수 있습니다.
                pass
        else:
            print(f"UDP 데이터 수신: {data}")
        return "UDP 데이터를 성공적으로 처리했습니다."

if __name__== "__main__":
    service = UDPIVService()
    service.start_udp_server()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n서버 종료 요청")
    finally:
        service.server_manager.stop_server()
        print("프로그램이 완전히 종료되었습니다.")
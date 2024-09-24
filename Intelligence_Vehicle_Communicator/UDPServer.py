import json
import threading
import sys
import os
import cv2
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.UDPConnection import UDPConnection

class UDPServer:
    def __init__(self, host='localhost', port=12345, data_handler=None):
        self.host = host
        self.port = port
        self.udp_connection = UDPConnection(host, port)
        self.running = False
        self.data_handler = data_handler or self.default_data_handler

    def start(self):
        self.udp_connection.create_socket()
        self.udp_connection.bind()
        print(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")
        
        self.running = True
        while self.running:
            try:
                data_type, data, address = self.udp_connection.receive_data()
                # print(f' ==> Line 29: \033[38;2;236;228;197m[data]\033[0m({type(data).__name__}) = \033[38;2;239;252;79m{data}\033[0m')
                # print(f' ==> Line 29: \033[38;2;151;13;153m[data_type]\033[0m({type(data_type).__name__}) = \033[38;2;3;110;17m{data_type}\033[0m')
                
                if data is None:
                    continue
                
                if isinstance(data, tuple) and len(data) == 2:
                    if isinstance(data[1], str) and data[1] == 'exit':
                        print(f"클라이언트 {address}가 정상적으로 연결 종료를 요청했습니다.")
                        continue
                
                # 외부 데이터 핸들러 호출
                response = self.data_handler(data_type, data, address)
                
                # 응답이 있으면 클라이언트에게 전송
                if response:
                    self.udp_connection.send_data(response, type(response).__name__, address=address)

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")

    def stop(self):
        self.running = False
        self.udp_connection.close()
        print("서버가 종료되었습니다.")

    @staticmethod
    def default_data_handler(data_type, data, client_address):
        print(f"클라이언트 {client_address}로부터 수신:")
        print(f"데이터 유형: {data_type}")
    
        if data_type == 2:  # 이미지 데이터
            identifier, image_data = data
            print(f"이미지 식별자: {identifier}")
            print(f"이미지 데이터 shape: {image_data.shape}")
        else:
            print(f"데이터: {data}")
        return None  # 기본적으로 응답을 보내지 않음


class UDPServerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UDPServerManager, cls).__new__(cls)
            cls._instance.server = None
        return cls._instance

    def start_server(self, host='localhost', port=12345, data_handler=None):
        if self.server is None:
            self.server = UDPServer(host, port, data_handler)
            server_thread = threading.Thread(target=self.server.start)
            server_thread.start()
        else:
            print("서버가 이미 실행 중입니다.")

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None
        else:
            print("실행 중인 서버가 없습니다.")


# 이미지 표시
def display_image(identifier, image_data):
    try:
        cv2.imshow(f"Image from {identifier}", image_data)
        cv2.waitKey(1)  # 1ms 동안 대기 (이미지 표시를 위해 필요)
    except Exception as e:
        print(f"이미지 표시 중 오류 발생: {e}")


# 사용 예시
def custom_data_handler(data_type, data, client_address):
    if data_type == 2:  # 이미지 데이터
        identifier, image_data = data
        print(f"이미지: {type(image_data)}")
        if isinstance(image_data, np.ndarray):
            threading.Thread(target=display_image, args=(identifier, image_data)).start()

        if identifier == 'IF':
            print("정면 카메라 이미지 수신")
        elif identifier == 'IL':
            print("차선 카메라 이미지 수신")
    else:
        print(f"클라이언트 {client_address}로부터 데이터 수신: {data}")

    return "데이터를 성공적으로 처리했습니다."


if __name__ == "__main__":
    manager = UDPServerManager()
    try:
        manager.start_server(data_handler=custom_data_handler)
        while True:
            user_input = input("서버를 종료하려면 'q'를 입력하세요...\n")
            if user_input.lower() == 'q':
                break

    except KeyboardInterrupt:
        print("\n서버 종료 요청")

    finally:
        manager.stop_server()
        print("프로그램이 완전히 종료되었습니다.")
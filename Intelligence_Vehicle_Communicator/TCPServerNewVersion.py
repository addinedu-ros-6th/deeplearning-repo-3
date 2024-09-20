import json
import socket
import threading
import sys
import os
import cv2
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPConnectionNewVersion import TCPConnection


class TCPServer:
    def __init__(self, host='localhost', port=12345, data_handler=None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.data_handler = data_handler or self.default_data_handler


    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)  # 1초 타임아웃 설정
        print(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")
        
        
        self.running = True
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
                self.clients.append(client_thread)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"클라이언트 연결 중 오류 발생: {e}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        for client in self.clients:
            if client.is_alive():
                client.join(timeout=2)
        
        print("서버가 종료되었습니다.")

    def handle_client(self, client_socket, client_address):
        tcp_connection = TCPConnection()
        tcp_connection.conn = client_socket
        print(f"클라이언트 {client_address} 연결됨")

        while self.running:
            try:
                data_type, data = tcp_connection.receive_data()
                print(f' ==> Line 67: \033[38;2;146;1;186m[data_type]\033[0m({type(data_type).__name__}) = \033[38;2;146;200;253m{data_type}\033[0m')
                print(f' ==> Line 67: \033[38;2;108;50;29m[data]\033[0m({type(data).__name__}) = \033[38;2;229;96;125m{data}\033[0m')
                
                if data is None:
                    break
                
                if isinstance(data, str) and data.lower() == 'exit':
                    print(f"클라이언트 {client_address}가 정상적으로 연결 종료를 요청했습니다.")
                    tcp_connection.send_data("연결이 정상적으로 종료되었습니다.", "str")
                    break

                # 외부 데이터 핸들러 호출
                response = self.data_handler(data_type, data, client_address)
                
                # 응답이 있으면 클라이언트에게 전송
                if response:
                    tcp_connection.send_data(response, type(response).__name__)

            except ConnectionResetError:
                print(f"클라이언트 {client_address}의 연결이 재설정되었습니다.")
                break

            except ConnectionAbortedError:
                print(f"클라이언트 {client_address}의 연결이 중단되었습니다.")
                break

            except Exception as e:
                print(f"클라이언트 {client_address} 처리 중 오류 발생: {e}")
                break

        print(f"클라이언트 {client_address} 연결 종료")
        client_socket.close()

    @staticmethod
    def default_data_handler(data_type, data, client_address):
        print(f"클라이언트 {client_address}로부터 수신:")
        print(f"데이터 유형: {type(data)}")
    
        if data_type == 2:  # 이미지 데이터
            identifier, image_data = data
            print(f"이미지 식별자: {identifier}")
            print(f"이미지 데이터 shape: {image_data.shape}")

        else:
            print(f"데이터: {data}")
        return None  # 기본적으로 응답을 보내지 않음


class TCPServerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TCPServerManager, cls).__new__(cls)
            cls._instance.server = None
        return cls._instance

    def start_server(self, host='localhost', port=12345, data_handler=None):
        if self.server is None:
            self.server = TCPServer(host, port, data_handler)
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
        # print(f"클라이언트 {client_address}로부터 이미지 수신:")

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
    manager = TCPServerManager()
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
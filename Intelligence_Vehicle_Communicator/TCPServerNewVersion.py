import socket
import threading
import sys
import os
import time
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPConnectionNewVersion import TCPConnection

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")
        
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
                    logging.error(f"클라이언트 연결 중 오류 발생: {e}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        for client in self.clients:
            if client.is_alive():
                client.join(timeout=2)
        
        logging.info("서버가 종료되었습니다.")

    def handle_client(self, client_socket, client_address):
        tcp_connection = TCPConnection()
        tcp_connection.conn = client_socket
        logging.info(f"클라이언트 {client_address} 연결됨")

        while self.running:
            try:
                data = tcp_connection.receive_data()
                if data is None:
                    break
                
                if isinstance(data, str) and data.lower() == 'exit':
                    logging.info(f"클라이언트 {client_address}가 정상적으로 연결 종료를 요청했습니다.")
                    tcp_connection.send_data("연결이 정상적으로 종료되었습니다.", "str")
                    break

                # 외부 데이터 핸들러 호출
                response = self.data_handler(data, client_address)
                
                # 응답이 있으면 클라이언트에게 전송
                if response:
                    tcp_connection.send_data(response, type(response).__name__)

            except ConnectionResetError:
                logging.warning(f"클라이언트 {client_address}의 연결이 재설정되었습니다.")
                break
            except ConnectionAbortedError:
                logging.warning(f"클라이언트 {client_address}의 연결이 중단되었습니다.")
                break
            except Exception as e:
                logging.error(f"클라이언트 {client_address} 처리 중 오류 발생: {e}")
                break

        logging.info(f"클라이언트 {client_address} 연결 종료")
        client_socket.close()

    @staticmethod
    def default_data_handler(data, client_address):
        logging.info(f"클라이언트 {client_address}로부터 수신:")
        logging.info(f"데이터 유형: {type(data)}")
        logging.info(f"데이터: {data}")
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
            logging.warning("서버가 이미 실행 중입니다.")

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None
        else:
            logging.warning("실행 중인 서버가 없습니다.")

# 사용 예시
def custom_data_handler(data, client_address):
    logging.info(f"커스텀 핸들러: 클라이언트 {client_address}로부터 {type(data)} 데이터 수신")
    # 데이터 처리 로직
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
        logging.info("\n서버 종료 요청")
    finally:
        manager.stop_server()
        logging.info("프로그램이 완전히 종료되었습니다.")
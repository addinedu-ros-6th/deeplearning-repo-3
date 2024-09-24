from datetime import datetime
import json
import queue
import signal
import threading
import time
import numpy as np
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.UDPConnection import UDPConnection

class UDPClient:
    def __init__(self, client_id, data_type, host='localhost', port=12345):
        self.client_id = client_id
        self.data_type = data_type  # 'image' or 'str' or ''
        self.udp_connection = UDPConnection(host, port)
        self.running = False
        self.thread = None
        self.data_queue = queue.Queue()

    def connect(self):
        self.udp_connection.create_socket()
        print(f"클라이언트 {self.client_id}가 UDP 소켓을 생성했습니다.")

    def send_data(self, data, identifier=''):
        try:
            self.udp_connection.send_data(data, self.data_type, identifier)
            # print(f"Client {self.client_id} sent {self.data_type} with identifier {identifier}")
        except Exception as e:
            print(f"Error sending {self.data_type}: {e}")

    def send_message(self, data, identifier=''):
        """Queue a message for sending"""
        self.queue_data(data)

    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.data_queue.get_nowait()
                if isinstance(data, tuple) and len(data) == 2:
                    self.send_data(data[0], data[1])
                else:
                    self.send_data(data)

            except queue.Empty:
                time.sleep(0.03)

    def start(self):
        self.connect()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        """스레드를 종료합니다"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.close()

    def close(self):
        """연결을 끊습니다"""
        try:
            # 종료 메시지 전송
            self.udp_connection.send_data("exit", "str")
        except Exception as e:
            print(f"Error during client shutdown: {e}")
        finally:
            self.udp_connection.close()

    def queue_data(self, data):
        self.data_queue.put(data)

class UDPClientManager:
    """싱글톤입니다. 인스턴트를 여러개 만들어도 1개의 인스턴트를 보장합니다"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UDPClientManager, cls).__new__(cls)
            cls._instance.clients = {}
            cls._instance.get_data_funcs = {}
            cls._instance.setup_signal_handler()
        return cls._instance
    
    def get_client(self, client_id, data_type, host='localhost', port=12345):
        if client_id in self.clients:
            print(f"기존 클라이언트 {client_id} 반환 중")
            return self.clients[client_id]
        
        else:
            print(f"새 클라이언트 {client_id} 추가 중")
            return self.add_client(client_id, data_type, host, port)
    
    def add_client(self, client_id, data_type, host='localhost', port=12345):
        if client_id not in self.clients:
            try:
                client = UDPClient(client_id, data_type, host, port)
                self.clients[client_id] = client
                print(f"클라이언트 {client_id} 추가됨")
                return client
            except Exception as e:
                print(f"클라이언트 {client_id} 추가 실패: {e}")
                return None
        else:
            print(f"클라이언트 {client_id}가 이미 존재함")
            return self.clients[client_id]

    def remove_client(self, client_id):
        """연결을 종료하고 스레드를 닫습니다"""
        if client_id in self.clients:
            client = self.clients[client_id]
            client.stop()
            del self.clients[client_id]
            print(f"클라이언트 {client_id} 제거됨")
        else:
            print(f"클라이언트 {client_id}이(가) 존재하지 않습니다.")

    def start_client(self, client_id):
        """스레드를 시작합니다"""
        if client_id in self.clients:
            client = self.clients[client_id]
            client.start()
            print(f"Started client {client_id}")
        else:
            print(f"클라이언트 {client_id}가 존재하지 않습니다.")

    def stop_client(self, client_id):
        "클라이언트를 중지합니다. 다만 self.clients에는 지우지 않아서 바로 start로 재활성가능합니다."
        if client_id in self.clients:
            client = self.clients[client_id]
            client.stop()
            print(f"중지된 클라이언트 {client_id}")
            
        else:
            print(f"클라이언트 {client_id}이(가) 존재하지 않습니다.")

    def stop_all_clients(self):
        print("stop_all_clients 메서드가 호출되었습니다.")
        for client_id, client in self.clients.items():
            print(f"클라이언트 {client_id} 중지 중...")
            client.stop()
        print("모든 클라이언트를 중지했습니다.")

    def setup_signal_handler(self):
        print("신호 핸들러 설정 중...")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        print("신호 핸들러 설정 완료")

    def signal_handler(self, sig, frame):
        print(f"\n신호 {sig}를 받았습니다. 모든 클라이언트를 중지하는 중...")
        self.stop_all_clients()

    def queue_data(self, client_id, data):
        if client_id in self.clients:
            client = self.clients[client_id]
            client.queue_data(data)
        else:
            print(f"클라이언트 {client_id}이(가) 존재하지 않습니다.")



# 아래는 예제 코드입니다.
if __name__ == "__main__":
    print("메인 프로그램 시작")
    
    def get_image():
        return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)
    
    def get_text():
        return f"Sample text data"
    
    manager = UDPClientManager()
    
    try:
        print("클라이언트 생성 및 시작")
        client1 = manager.get_client("test_image_client", 'image')
        client2 = manager.get_client("test_text_client", 'str')
        client1.start()
        client2.start()
        
        for _ in range(10):
            time.sleep(1)
            client1.queue_data((get_image(), 'IF'))
            client1.queue_data((get_image(), 'IL'))
            client2.queue_data(get_text())
        print("모든 메시지 전송 완료")
    
    except KeyboardInterrupt:
        print("\n키보드 인터럽트를 받았습니다.")
    
    finally:
        manager.stop_all_clients()
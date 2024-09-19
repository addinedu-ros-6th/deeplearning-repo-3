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
from Intelligence_Vehicle_Communicator.TCPConnectionNewVersion import TCPConnection

class TCPClient:
    def __init__(self, client_id, data_type, host='localhost', port=12345, max_retries=120, retry_delay=1):
        self.client_id = client_id
        self.data_type = data_type  # 'image' or 'str' or 'json'
        self.tcp_connection = TCPConnection(host, port)
        self.running = False
        self.thread = None
        self.data_queue = queue.Queue()

        # 최대 120초 동안 1초에 한번씩 서버 오픈 되기를 기다립니다.
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def connect(self):
        if not self.connect_with_retry():
            raise ConnectionError("여러 번 시도한 후 서버에 연결하지 못했습니다.")
    
    def connect_with_retry(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.tcp_connection.connect_to_server()
                print(f"클라이언트 {self.client_id}가 서버에 성공적으로 연결되었습니다.")
                return True
            except ConnectionRefusedError:
                print(f"연결 시도 {retries + 1}에 실패했습니다. 서버가 실행되고 있지 않을 수 있습니다. {self.retry_delay}초 후에 재시도 중...")
                time.sleep(self.retry_delay)
                retries += 1
        print(f"{self.max_retries} 시도 후 연결에 실패했습니다. 서버가 실행 중인지 확인하세요.")
        return False
    

    def send_data(self, data):
        try:
            self.tcp_connection.send_data(data, self.data_type)
            print(f"Client {self.client_id} sent {self.data_type}")

        except Exception as e:
            print(f"Error sending {self.data_type}: {e}")
            print(f"오류 유형: {type(e).__name__}")
            print(f"오류 상세 정보: {str(e)}")



    def send_message(self, data):
        """Queue a message for sending"""
        self.queue_data(data)


    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.data_queue.get_nowait() # queue에 데이터가 있을때만 전송한다.
                self.send_data(data)
            except queue.Empty:
                time.sleep(0.03)  # queue에 데이터가 없으면 대기한다. 대충 30프레임으로 맞춰놓음. 

    def start(self):
        # 클라이언트마다 개별 스레드에서 동작한다.
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
        """서버와 연결을 끊습니다"""
        try:
            # 종료 메시지 전송
            self.tcp_connection.send_data("exit", "str")
            # 서버로부터의 응답 대기
            response = self.tcp_connection.receive_data()
            if response:
                print(f"Server response on exit: {response}")
        except Exception as e:
            print(f"Error during client shutdown: {e}")
        finally:
            self.tcp_connection.close()
    
    def queue_data(self, data):
        self.data_queue.put(data)


class TCPClientManager:
    """싱글톤입니다. 인스턴트를 여러개 만들어도 1개의 인스턴트를 보장합니다"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TCPClientManager, cls).__new__(cls)
            cls._instance.clients = {}
            cls._instance.get_data_funcs = {}
            cls._instance.setup_signal_handler()
        return cls._instance
    
    def get_client(self, client_id, data_type, host='localhost', port=12345, max_retries=120, retry_delay=1):
        if client_id in self.clients:
            print(f"기존 클라이언트 {client_id} 반환 중")
            return self.clients[client_id]
        
        else:
            print(f"새 클라이언트 {client_id} 추가 중")
            return self.add_client(client_id, data_type, host, port, max_retries=120, retry_delay=1)
    
    def add_client(self, client_id, data_type, host='localhost', port=12345, max_retries=120, retry_delay=1):
        if client_id not in self.clients:
            try:
                client = TCPClient(client_id, data_type, host, port, max_retries, retry_delay)
                self.clients[client_id] = client
                print(f"클라이언트 {client_id} 추가됨")
                return client
            except ConnectionError as e:
                print(f"클라이언트 {client_id} 추가 실패: {e}")
                return None
        else:
            print(f"클라이언트 {client_id}가 이미 존재함")
            return self.clients[client_id]

    def remove_client(self, client_id):
        """서버와 연결을 종료하고 스레드를 닫습니다"""
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
            print(f"클라이언트 {client_id}이(가) 존재하지 않습니다.t")

    def stop_all_clients(self):
        print("stop_all_clients 메서드가 호출되었습니다.")
        for client_id, client in self.clients.items():
            print(f"클라이언트 {client_id} 중지 중...")
            client.stop()
        print("모든 클라이언트를 중지했습니다.")


    def setup_signal_handler(self):
        print("신호 핸들러 설정 중...")
        signal.signal(signal.SIGINT, self.signal_handler) # SIGINT: 보통 사용자가 키보드에서 Ctrl+C를 누를 때 발생
        signal.signal(signal.SIGTERM, self.signal_handler) # SIGTERM: 일반적으로 시스템이나 다른 프로세스가 이 프로그램을 종료하려고 할 때 발생
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



# 아래는 예제 코드입니다. ##############################################################################################
# 주의 사항: Server가 먼저 열려있어야 합니다. 
if __name__ == "__main__":
    print("메인 프로그램 시작")
    
    # 테스트를 위한 이미지와 텍스트를 만드는 함수
    def get_image():
        return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)
    
    def get_text():
        return f"Sample text data"
    
    # 싱글톤인 TCPClientManager를 하나 추가합니다.
    manager = TCPClientManager()
    
    # 이미지와 텍스트를 보내는 클라이언트를 개별적으로 만듭니다.
    try:
        print("클라이언트 생성 및 시작")
        client1 = manager.get_client("test_image_client", 'json')
        client2 = manager.get_client("test_text_client", 'str')
        client1.start()
        client2.start()
        
        # JSON 형식으로 이미지 전송
        client1.send_message({'key': 'IL', 'image': get_image()})
        client2.send_message(get_text())
        
        for _ in range(10):
            client1.send_message({'key': 'IL', 'image': get_image()})
            client2.send_message(get_text())
            time.sleep(1)
        print("모든 메시지 전송 완료")
    
    except KeyboardInterrupt:
        print("\n키보드 인터럽트를 받았습니다.")
    
    finally:
        manager.stop_all_clients()
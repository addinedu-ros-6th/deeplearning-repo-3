from typing import Any, Callable
from flask import Flask, request, jsonify
import requests
from threading import Thread
import socket

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class FlaskClient(metaclass = SingletonMeta):

    def __init__(self, client_id, port):
        self.client_id = client_id
        self.port = port
        self.app = Flask(__name__)

        # 클라이언트의 메시지 수신 라우트 설정
        self.setup_routes()
        self.run()
        

    def setup_routes(self):
        self.app.route('/receive_data', methods=['POST'])(self.receive_data)

    def set_callback(self, callback: Callable[[str, Any], None]):
        self.callback = callback

    def receive_data(self):
        data = request.json

        from_client = data.get('from')
        receive_data = data.get('data')
        recevie_key = data.get('key')
        print('\033[91m'+'recevie_key: ' + '\033[92m', recevie_key, '\033[0m')

        # print(f"Received data from {from_client}: {data}")
        if self.callback:
            self.callback(from_client, recevie_key, receive_data)
        return jsonify({"status": "success", "message": "Data received"}), 200


    # 다른 클라이언트로 메시지를 전송
    def send_data(self, to_client_url, key, data):

        payload = {
            "from": self.client_id,
            "key": key,
            "data": data
        }

        try:
            response = requests.post(f"{to_client_url}/receive_data", json=payload)
            print(f"Response from {to_client_url}: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")


    # 클라이언트 실행 (별도의 스레드에서 Flask 실행)
    def run(self):
        Thread(target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)).start()

    def is_port_open(self, host, ports):
        """해당 호스트의 포트가 열려 있는지 확인"""
        if len(ports) == 0:
            print("All servers are open.")
            return True

        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((host, port))
                if result != 0:
                    print(f"The {port} is not yet open")
                    return False  # 하나라도 닫혀있으면 False 반환
        print("All servers are open.")
        return True  # 모든 포트가 열려있으면 True 반환



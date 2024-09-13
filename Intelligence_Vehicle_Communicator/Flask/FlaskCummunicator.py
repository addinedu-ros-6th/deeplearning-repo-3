from typing import Any
from flask import Flask, request, jsonify
import requests
from threading import Thread

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
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

    def setup_routes(self):
        self.app.route('/receive_data', methods=['POST'])(self.receive_data)


    def receive_data(self):
        data = request.json
        from_client = data.get('from')

        data = data.get('data')
        print(f"Received data from {from_client}: {data}")
        return jsonify({"status": "success", "data": "Data received"}), 200

    # 다른 클라이언트로 메시지를 전송
    def send_data(self, to_client_url, data):
        data = {
            "from": self.client_id,
            "data": data
        }
        try:
            response = requests.post(f"{to_client_url}/receive_data", json=data)
            print(f"Response from {to_client_url}: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")

    # 클라이언트 실행 (별도의 스레드에서 Flask 실행)
    def run(self):
        Thread(target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)).start()


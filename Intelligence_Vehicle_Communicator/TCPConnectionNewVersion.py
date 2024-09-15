import socket
import struct
import pickle
import threading
import numpy as np
import select

class TCPConnection:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.sock = None
        self.conn = None

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"{self.host}:{self.port}에 연결 성공.")

    def send_data(self, data, data_type):
        if self.sock is None and self.conn is None:
            raise ConnectionError("연결이 설정되지 않았습니다.")
        
        if data_type == 'str':
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
        elif data_type == 'image':
            data = pickle.dumps(data)
        else:
            raise ValueError("지원하지 않는 데이터 유형입니다.")

        data_length = len(data)
        packed_length = struct.pack('!I', data_length)
        packed_type = struct.pack('!I', 1 if data_type == 'str' else 2)

        try:
            connection = self.conn if self.conn else self.sock
            connection.sendall(packed_type + packed_length + data)
        except Exception as e:
            print(f"데이터 전송 오류: {e}")
            raise

    def receive_data(self, timeout=5):
        if self.sock is None and self.conn is None:
            raise ConnectionError("연결이 설정되지 않았습니다.")
        
        try:
            connection = self.conn if self.conn else self.sock
            ready = select.select([connection], [], [], timeout)
            if ready[0]:
                packed_type = connection.recv(4)
                if not packed_type:
                    return None
                data_type = struct.unpack('!I', packed_type)[0]

                packed_length = connection.recv(4)
                if not packed_length:
                    return None
                data_length = struct.unpack('!I', packed_length)[0]

                data = b""
                while len(data) < data_length:
                    chunk = connection.recv(min(4096, data_length - len(data)))
                    if not chunk:
                        return None
                    data += chunk

                if data_type == 1:
                    return data.decode('utf-8')
                elif data_type == 2:
                    try:
                        return pickle.loads(data)
                    except pickle.UnpicklingError:
                        print("이미지 데이터 언피클링 오류")
                        return None
                else:
                    raise ValueError("알 수 없는 데이터 유형입니다.")
            else:
                print("데이터 수신 타임아웃")
                return None
        except Exception as e:
            print(f"데이터 수신 오류: {e}")
            return None


    def close(self):
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()
        self.conn = None
        self.sock = None
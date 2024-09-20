import base64
import binascii
import json
import socket
import struct
import pickle
import threading
import cv2
import numpy as np
import select

class TCPConnection:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.sock = None
        self.conn = None
        self.socket_type = None

    def connect_to_server(self, sock_type=socket.SOCK_STREAM):
        self.socket_type = sock_type
        self.sock = socket.socket(socket.AF_INET, sock_type)

        if self.socket_type == socket.SOCK_STREAM:
            self.sock.connect((self.host, self.port))
            print(f"TCP 연결: {self.host}:{self.port}에 연결 성공.")
        else:
            print(f"UDP 소켓 생성: {self.host}:{self.port}")


    def send_data(self, data, data_type, identifier=''):
        if self.socket_type is None:
            raise ConnectionError("연결 유형이 설정되지 않았습니다.")
        
        if data_type == 'str':
            if not isinstance(data, bytes):
                data = pickle.dumps((identifier, data))
        elif data_type == 'image':
            if isinstance(data, np.ndarray):
                data = cv2.imencode('.jpg', data)[1]
                data = pickle.dumps((identifier, data))
        else:
            raise ValueError("지원하지 않는 데이터 유형입니다.")

        data_length = len(data)
        packed_length = struct.pack('!I', data_length)
        packed_type = struct.pack('!I', 1 if data_type == 'str' else 2)

        try:
            if self.socket_type == socket.SOCK_STREAM:
                connection = self.conn if self.conn else self.sock
                connection.sendall(packed_type + packed_length + data)
            else:
                self.sock.sendto(packed_type + packed_length + data, (self.host, self.port))

        except BrokenPipeError:
            print("연결이 끊어졌습니다. 재연결을 시도합니다.")
            self.connect_to_server(self.socket_type)
            self.send_data(data, data_type, identifier)  

        except Exception as e:
            print(f"데이터 전송 오류: {e}")
            raise



    def receive_data(self, timeout=5):
        if self.sock is None and self.conn is None:
            raise ConnectionError("연결이 설정되지 않았습니다.")
        
        try:
            if self.socket_type == socket.SOCK_STREAM:
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
                else:
                    print("데이터 수신 타임아웃")
                    return None
            else:  # UDP
                self.sock.settimeout(timeout)
                data, addr = self.sock.recvfrom(65507)  # UDP의 최대 패킷 크기
                if not data:
                    return None
                data_type = struct.unpack('!I', data[:4])[0]
                data_length = struct.unpack('!I', data[4:8])[0]
                data = data[8:]

            # 공통 데이터 처리 로직
            if data_type == 1:  # 문자열 데이터
                identifier, value = pickle.loads(data)
                return 1, (identifier, str(value))
            elif data_type == 2:  # 이미지 데이터
                try:
                    identifier, image_data = pickle.loads(data)
                    return 2, (identifier, image_data)
                except pickle.UnpicklingError:
                    print("이미지 데이터 언피클링 오류")
                    return None
            else:
                raise ValueError("알 수 없는 데이터 유형입니다.")

        except socket.timeout:
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
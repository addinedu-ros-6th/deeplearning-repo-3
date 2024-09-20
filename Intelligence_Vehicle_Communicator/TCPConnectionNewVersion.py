import base64
import binascii
import json
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

    def send_data(self, data, data_type, identifier=''):
        if self.sock is None and self.conn is None:
            raise ConnectionError("연결이 설정되지 않았습니다.")
        
        if data_type == 'str':
            if not isinstance(data, bytes):
                data = pickle.dumps((identifier, data))

        elif data_type == 'image':
            data = pickle.dumps((identifier, data))

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
            # select.select
            # - I/O 멀티플렉싱을 위해 사용되는 Python의 저수준 함수
            # - 이 함수는 여러 소켓이나 파일 디스크립터를 동시에 모니터링하고, 
            # - 그 중 하나라도 읽기, 쓰기 또는 예외 상태가 되면 알려줍니다.
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
                    # data_type, data = identifier, data.decode('utf-8')
                    identifier, str = pickle.loads(data)
                    print(f' ==> Line 84: \033[38;2;119;23;116m[identifier]\033[0m({type(identifier).__name__}) = \033[38;2;243;234;167m{identifier}\033[0m')
                    print(f' ==> Line 84: \033[38;2;175;88;199m[image_data]\033[0m({type(str).__name__}) = \033[38;2;144;229;107m{str}\033[0m')
                    
                    return 1, (identifier, data.decode('utf-8'))
                elif data_type == 2:
                    try:
                        identifier, image_data = pickle.loads(data)
                        return 2, (identifier, image_data)
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
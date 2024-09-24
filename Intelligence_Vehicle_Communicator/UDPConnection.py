import struct
import pickle
import socket
import uuid

import cv2
import numpy as np

MAX_PACKET_SIZE = 60000  # UDP 패킷의 최대 크기를 60KB로 설정

class UDPConnection:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        print(f' ==> Line 13: \033[38;2;30;136;101m[host]\033[0m({type(host).__name__}) = \033[38;2;82;143;131m{host}\033[0m')
        self.port = port
        print(f' ==> Line 15: \033[38;2;242;133;230m[port]\033[0m({type(port).__name__}) = \033[38;2;145;192;100m{port}\033[0m')
        self.sock = None

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self):
        self.sock.bind((self.host, self.port))

    def send_data(self, data, data_type, identifier='', address=None):
        if self.sock is None:
            raise ConnectionError("소켓이 생성되지 않았습니다.")
        
        if data_type == 'str':
            data_type_int = 1
            if not isinstance(data, bytes):
                data = pickle.dumps((identifier, data))
        elif data_type == 'image':
            data_type_int = 2
            if not isinstance(data, bytes):
                data = pickle.dumps((identifier, data))
        else:
            raise ValueError("지원하지 않는 데이터 유형입니다.")

        # 큰 데이터를 여러 패킷으로 나누어 전송
        chunks = [data[i:i+MAX_PACKET_SIZE] for i in range(0, len(data), MAX_PACKET_SIZE)]
        message_id = str(uuid.uuid4())  # 고유한 메시지 ID 생성
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            header = struct.pack('!I', data_type_int) + struct.pack('!I', len(chunk)) + message_id.encode() + struct.pack('!II', i, total_chunks)
            try:
                if address:
                    self.sock.sendto(header + chunk, address)
                else:
                    self.sock.sendto(header + chunk, (self.host, self.port))
            except Exception as e:
                print(f"데이터 전송 오류: {e}")
                raise

    def receive_data(self, buffer_size=65507):
        if self.sock is None:
            raise ConnectionError("소켓이 생성되지 않았습니다.")
        
        chunks = {}
        while True:
            try:
                packet, address = self.sock.recvfrom(buffer_size)
                data_type = struct.unpack('!I', packet[:4])[0]
                chunk_size = struct.unpack('!I', packet[4:8])[0]
                message_id = packet[8:44].decode()
                chunk_index, total_chunks = struct.unpack('!II', packet[44:52])
                chunk_data = packet[52:]

                if message_id not in chunks:
                    chunks[message_id] = {}
                chunks[message_id][chunk_index] = chunk_data

                if len(chunks[message_id]) == total_chunks:
                    # 모든 청크를 받았으면 데이터를 재구성
                    data = b''.join(chunks[message_id][i] for i in range(total_chunks))
                    del chunks[message_id]  # 메모리 정리

                    if data_type == 1:
                        identifier, value = pickle.loads(data)
                        return 1, (identifier, value), address
                    elif data_type == 2:
                        try:
                            identifier, image_data = pickle.loads(data)

                            # 이미지 데이터가 이미 numpy 배열인 경우 바로 반환
                            if isinstance(image_data, np.ndarray):
                                return 2, (identifier, image_data), address
                            
                            # JPEG 데이터인 경우 디코딩
                            elif isinstance(image_data, tuple) and len(image_data) == 2:
                                decoded_image = cv2.imdecode(np.frombuffer(image_data[1], np.uint8), cv2.IMREAD_COLOR)
                                # cv2.imshow("lane", decoded_image)
                                # cv2.waitKey(100)

                                return 2, (identifier, decoded_image), address
                        
                            else:
                                print(f"알 수 없는 이미지 데이터 형식: {type(image_data)}")
                                return None, None, address
                            
                        except pickle.UnpicklingError:
                            print("이미지 데이터 언피클링 오류")
                            return None, None, address
                    else:
                        raise ValueError("알 수 없는 데이터 유형입니다.")

            except Exception as e:
                print(f"UDP 데이터 수신 오류: {e}")
                return None, None, None

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None
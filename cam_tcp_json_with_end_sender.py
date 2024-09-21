import socket
import cv2
import numpy as np
import json
import base64
from threading import Thread, Lock
import time

class FrameBuffer:
    def __init__(self):
        self.frames = [None, None]  # 두 개의 카메라 프레임을 위한 버퍼
        self.lock = Lock()

    def update(self, idx, frame):
        with self.lock:
            self.frames[idx] = frame

    def get(self, idx):
        with self.lock:
            return self.frames[idx]

def webcam(frame_buffer, idx):
    capture = cv2.VideoCapture(idx)
    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                continue
            
            # 이미지 인코딩
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = np.array(imgencode)
            stringData = data.tobytes()
            
            # Base64로 인코딩하여 JSON으로 변환
            json_data = json.dumps({
                'type': 'image',
                'index': idx,
                'image': base64.b64encode(stringData).decode('utf-8')
            })
            
            frame_buffer.update(idx, json_data)
    finally:
        capture.release()

def handle_client(client_socket, addr, frame_buffer):
    print('Connected by:', addr)
    try:
        while True:
            # 첫 번째 카메라의 프레임을 전송
            frame1 = frame_buffer.get(0)
            if frame1 is not None:
                client_socket.sendall((frame1 + '\n').encode('utf-8'))
            else:
                client_socket.sendall(json.dumps({'type': 'image', 'index': 0, 'image': ''}).encode('utf-8') + b'\n')

            # 약간의 딜레이를 주어 두 번째 카메라 프레임도 전송
            time.sleep(0.03)

            # 두 번째 카메라의 프레임을 전송
            frame2 = frame_buffer.get(1)
            if frame2 is not None:
                client_socket.sendall((frame2 + '\n').encode('utf-8'))
            else:
                client_socket.sendall(json.dumps({'type': 'image', 'index': 1, 'image': ''}).encode('utf-8') + b'\n')

            time.sleep(0.03)  # 약 30fps로 제한
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print('Disconnected by', addr)
        client_socket.close()


def start_camera_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    frame_buffer = FrameBuffer()

    # 두 개의 카메라 스레드 시작
    webcam_thread_0 = Thread(target=webcam, args=(frame_buffer, 0))  # 첫 번째 카메라
    webcam_thread_1 = Thread(target=webcam, args=(frame_buffer, 1))  # 두 번째 카메라
    webcam_thread_0.start()
    webcam_thread_1.start()

    print('Camera Server Started')

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = Thread(target=handle_client, args=(client_socket, addr, frame_buffer))
            client_thread.start()
    except KeyboardInterrupt:
        print("Camera server is shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_camera_server('192.168.0.11', 4002)  # 서버 실행
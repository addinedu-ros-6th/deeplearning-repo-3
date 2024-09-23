import socket
import cv2
import numpy as np
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
            
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            
            data = np.array(imgencode)
            stringData = data.tobytes()
            
            frame_buffer.update(idx, stringData)
    finally:
        capture.release()

def handle_client(client_socket, addr, frame_buffer):
    print('Connected by:', addr)
    try:
        while True:
            # 첫 번째 카메라의 프레임을 전송
            frame1 = frame_buffer.get(0)
            if frame1 is not None:
                # "IF" 접두사 추가
                data_to_send = b"IF" + str(len(frame1)).ljust(16).encode() + frame1
                client_socket.send(data_to_send)
            else:
                client_socket.send(b"IF" + b"0".ljust(16).encode())
            
            # 약간의 딜레이를 주어 두 번째 카메라 프레임도 전송
            time.sleep(0.03)

            # 두 번째 카메라의 프레임을 전송
            frame2 = frame_buffer.get(1)
            if frame2 is not None:
                # "IL" 접두사 추가
                data_to_send = b"IL" + str(len(frame2)).ljust(16).encode() + frame2
                client_socket.send(data_to_send)
            else:
                client_socket.send(b"IL" + b"0".ljust(16).encode())
            
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

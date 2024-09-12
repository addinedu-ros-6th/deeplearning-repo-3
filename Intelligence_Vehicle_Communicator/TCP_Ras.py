import socket
import cv2
import numpy as np
from threading import Thread, Lock
import time

class FrameBuffer:
    def __init__(self):
        self.frames = [None, None, None]  # 두 개의 프레임 버퍼
        self.lock = Lock()

    def update(self, idx, frame):
        with self.lock:
            self.frames[idx] = frame

    def get(self, idx):
        with self.lock:
            return self.frames[idx]

def webcam(frame_buffer, idx):
    capture = cv2.VideoCapture(idx)
    # while True:
    #     ret, frame = capture.read()
    #     if not ret:
    #         continue
        
    #     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    #     result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        
    #     data = np.array(imgencode)
    #     stringData = data.tobytes()
        
    #     frame_buffer.update(idx, stringData)
    
    # capture.release()
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
            data = client_socket.recv(1024)
            if not data:
                break
            
            # 클라이언트가 요청한 카메라 인덱스
            camera_index = int(data.decode().strip())
            frame = frame_buffer.get(camera_index)
            if frame is not None:
                client_socket.send(str(len(frame)).ljust(16).encode())
                client_socket.send(frame)
            else:
                client_socket.send(b"0".ljust(16).encode())
            
            time.sleep(0.03)  # 약 30 fps로 제한
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print('Disconnected by', addr)
        client_socket.close()

def main():
    HOST = '172.20.10.5'
    PORT = 4002

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    frame_buffer = FrameBuffer()

    # 두 개의 웹캠 스레드 시작
    webcam_thread_0 = Thread(target=webcam, args=(frame_buffer, 0))
    webcam_thread_1 = Thread(target=webcam, args=(frame_buffer, 1))
    webcam_thread_0.start()
    webcam_thread_1.start()

    print('Server Started')

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = Thread(target=handle_client, args=(client_socket, addr, frame_buffer))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()

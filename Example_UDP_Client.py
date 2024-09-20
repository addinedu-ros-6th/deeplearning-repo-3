import os
import random
import socket
import sys
import threading
import time
import cv2
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.UDPClient import UDPClientManager


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_image():
    video_path = 'Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4'
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame = random.randint(0, frame_count - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        return frame
    else:
        return np.zeros((480, 640, 3), dtype=np.uint8)

def get_text():
    return "Hello"

HOST = 'localhost'
PORT = 4001

def start_udp_client():
    try:
        client_manager = UDPClientManager()
        client1 = client_manager.get_client("image_client", 'image', host=HOST, port=PORT)
        client1.start()
        time.sleep(1)  # 1초 대기

        for _ in range(10):
            time.sleep(1)
            try:
                image = get_image()
                client1.queue_data((image, 'lane'))  # 차선 카메라 이미지
                print(f"이미지 전송 완료: shape {image.shape}, dtype {image.dtype}")
            except Exception as e:
                print(f"이미지 전송 중 오류 발생: {e}")
        print("모든 메시지 전송 완료")


    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지. 클라이언트를 종료합니다...")
        client_manager.stop_all_clients()
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        client_manager.stop_all_clients()

if __name__== "__main__":
    start_udp_client()
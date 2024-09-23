import os
import random
import socket
import sys
import threading
import time
import cv2
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager


HOST = '192.168.0.22'
PORT = 4001

def start_tcp_client():
    time.sleep(2)  # 서버가 시작될 때까지 잠시 대기
    try:
        client_manager = TCPClientManager()
        client1 = client_manager.get_client("image_client", 'image', host=HOST, port=PORT)
        client1.start()
        
        for _ in range(10):
            time.sleep(1)
            client1.queue_data((get_image(), 'lane'))
        print("모든 메시지 전송 완료")

    except Exception as e:
        print(f"클라이언트 오류 발생: {e}")
    except KeyboardInterrupt:
        print("사용자 종료 요청")    
    finally:
        if 'client_manager' in locals():
            client_manager.stop_all_clients()

def get_image():
    capture = cv2.VideoCapture(0)

    ret, frame = capture.read()
    if not ret:
        pass
    return frame
if __name__== "__main__":
    # 쓰레드로 실행
    start_tcp_client()
    

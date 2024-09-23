# import os
# import sys
# import threading
# import time
# import numpy as np
# current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
# relative_path = os.path.join(current_dir, '../..')  # 상위 폴더로 이동
# sys.path.append(relative_path)
# from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager


# def get_image():
#     return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)

# def get_text():
#     return "Hello"

# HOST = 'localhost'
# PORT = 4001

# def start_tcp_client():
#     try:
#         client_manager = TCPClientManager()
#         client1 = client_manager.get_client("image_client", 'image', host=HOST, port=PORT)
#         client1.start()

#         for _ in range(10):
#             time.sleep(1)
#             client1.queue_data((get_image(), 'obstacle'))  # 정면 카메라 이미지
#             client1.queue_data((get_image(), 'lane'))  # 차선 카메라 이미지
#         print("모든 메시지 전송 완료")

#     except KeyboardInterrupt:
#         print("\n키보드 인터럽트 감지. 서버를 종료합니다...")
#         client_manager.stop_all_clients()

#     finally:
#         client_manager.stop_all_clients()


# if __name__== "__main__":
#     # 쓰레드로 실행
#     threading.Thread(target=start_tcp_client).start()

import os
import sys
import threading
import time
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClientManager


def get_image():
    return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)

def get_text():
    return "Hello"

HOST = '192.168.0.12'
PORT = 4001

def start_tcp_client(client_manager):
    try:
        client1 = client_manager.get_client("image_client", 'image', host=HOST, port=PORT)
        client1.start()

        for _ in range(10):
            time.sleep(1)
            client1.queue_data((get_image(), 'obstacle'))  # 정면 카메라 이미지
            client1.queue_data((get_image(), 'lane'))  # 차선 카메라 이미지
        print("모든 메시지 전송 완료")

    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지. 서버를 종료합니다...")
        client_manager.stop_all_clients()

    finally:
        client_manager.stop_all_clients()


if __name__ == "__main__":
    # 메인 스레드에서 TCPClientManager 인스턴스 생성
    client_manager = TCPClientManager()
    
    # 클라이언트 시작을 쓰레드로 실행
    threading.Thread(target=start_tcp_client, args=(client_manager,)).start()

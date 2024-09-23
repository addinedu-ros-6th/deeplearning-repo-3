import datetime
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
import time
import socket

import numpy as np
import cv2

import requests
import serial
import threading
 
from Intelligence_Vehicle_Communicator.TCPServerNewVersion import TCPServerManager, TCPServer
from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClient, TCPClientManager
from Intelligence_Vehicle_Communicator.UDPClient import UDPClientManager
from Intelligence_Vehicle_Communicator.UDPServer import UDPServerManager

def read_encoder():
    # 아두이노로부터 엔코더 값을 읽어옴
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        return line
    return None

def motor_forward(speed):
    command = f'F{speed}\n'.encode()
    ser.write(command)  # 'F' + 속도 값 전송

def motor_backward(speed):
    command = f'B{speed}\n'.encode()
    ser.write(command)  # 'B' + 속도 값 전송

def motor_stop():
    ser.write(b'S\n')  # 'S' 전송 (정지)

def right_motor_correction(right_motor_correction):
    command = f'C{right_motor_correction}\n'.encode()
    ser.write(command)  # 'C' + 오른쪽 보정 값 전송

def encoder_reset():
    ser.write(b'E\n')  # 엔코더 0으로 초기화

# 엔코더 값을 0.1초마다 읽고 출력하는 함수
def encoder_monitor():
    # encoder_url = 'http://192.168.0.12:4100/post_encoder'
    pre_encoder_value =0
    while True:
        encoder_value = read_encoder()
        if encoder_value:

            parts = encoder_value.split()
            # "L:" 뒤의 값을 가져와서 int로 변환
            L_encoder = int(parts[0].replace('L:', ''))
            
            # "R:" 뒤의 값을 가져와서 int로 변환
            R_encoder = int(parts[1].replace('R:', ''))

            mean_encoder_value = (abs(L_encoder)+abs(R_encoder))/2
            
            delta_encoder = mean_encoder_value-pre_encoder_value
            cur_speed = delta_encoder*20.42/2500

            client_speed.queue_data((str(cur_speed),'speed'))
            pre_encoder_value = mean_encoder_value
        time.sleep(0.1)  # 0.1초마다 엔코더 값 읽기

def fetch_commands(command):
    global pre_command
    try:
        # 명령을 파싱하여 모터 제어 함수 호출
        def process_command(cmd):
            if cmd[0] == 'F':
                speed = int(cmd[1:])  # 속도 값 추출
                motor_forward(speed)
                print(f"모터 전진 중 - 속도: {speed}")
            elif cmd[0] == 'B':
                speed = int(cmd[1:])  # 속도 값 추출
                motor_backward(speed)
                print(f"모터 후진 중 - 속도: {speed}")
            elif cmd[0] == 'S':
                motor_stop()
                print("모터 정지")
            elif cmd[0] == 'C':
                right_motor_correction_value = int(cmd[1:])  # 오른쪽 보정 값 추출
                right_motor_correction(right_motor_correction_value)
                print(f"오른 모터 보정값: {right_motor_correction_value}")
            elif cmd[0] == 'E':
                encoder_reset()
                print("엔코더 리셋")

        # 현재 명령을 처리
        process_command(command)
        
        # 'C' 또는 'E'일 경우, 이전 명령도 처리
        if command[0] in ['C', 'E']:
            process_command(pre_command)

        # 현재 명령을 이전 명령으로 저장
        else:
            pre_command = command

    except requests.RequestException as e:
        print(f"GET 요청 중 오류 발생: {e}")

    command_error_flag = not command_error_flag
    time.sleep(0.1)  # 5초마다 GET 요청

def custom_data_handler(data_type, data, client_address):
    if data_type == 1:  # 스트링 데이터
        identifier, str_data = data
        print(f"텍스트: {type(str_data)}")
    
        if identifier == 'speed':
            print("정면 카메라 이미지 수신")
        else:
            print("error identifier")

        if data[:2] == "ER":
            command = "C"+data[2:]
        elif data[:2] == "DF":
            command == "F"+data[2:]
        elif data[:2] == "ST":
            command == "S"
        fetch_commands(command)

        print(data)
    else:
        print(f"클라이언트 {client_address}로부터 데이터 수신: {data}")

    return "데이터를 성공적으로 처리했습니다."



# def handle_receive_tcp_data(data,client_address):
#     if data[:2] == "ER":
#         command = "C"+data[2:]
#     elif data[:2] == "DF":
#         command == "F"+data[2:]
#     elif data[:2] == "ST":
#         command == "S"

#     fetch_commands(command)

#     print(data)

# def start_tcp_client(client_manager):
#     try:
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

# def get_image():
#     return np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)


def send_cam_frame():

    try:
        while True:

            lane_frame = get_lane_frame()
            front_frame = get_front_frame()

            encode_param_lane = cv2.imencode('.jpg', lane_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            client_lane.queue_data((encode_param_lane,'lane'))

            encode_param_front = cv2.imencode('.jpg', front_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            cleint_front.queue_data((encode_param_front,'obstacle'))

            time.sleep(0.05)
        # speed_client.queue_data((get_speed(),'speed'))
        print("모든 메시지 전송 완료")

    except Exception as e:
        print(f"클라이언트 오류 발생: {e}")
    except KeyboardInterrupt:
        print("사용자 종료 요청")    
    # finally:
    #     if 'client_manager' in locals():
    #         # client_manager.stop_all_clients()

def resize_frame(frame):
    frame_width, frame_height = 640, 480
    decimg1 = cv2.resize(frame, (frame_width, frame_height))
    return decimg1

def get_lane_frame():
    ret, frame = lane_cam.read()
    if not ret:
        pass
    frame = resize_frame(frame)
    return frame

def get_front_frame():
    ret, frame = front_cam.read()
    if not ret:
        pass
    frame = resize_frame(frame)
    return frame

# def get_speed():
#     return cur_speed

if __name__ == "__main__":
    lane_cam = cv2.VideoCapture(0)
    front_cam = cv2.VideoCapture(1)
    # 만약 위의 인덱스로 열리지 않는다면 아래를 시도해 보세요
    # front_cam = cv2.VideoCapture(2)  # 또는 cv2.VideoCapture('/dev/video2')

    # host = '192.168.0.11'  # 서버를 실행할 IP 주소
    host = '192.168.26.178'
    port = 4002  # 서버 포트
#___________________________________________________________-
    # HOST='192.168.0.22' # 클라이언트 전송 할 ip
    HOST = '192.168.26.136'
    PORT= 4001 #클라이언트 전송 포트 
    # 아두이노가 연결된 시리얼 포트와 통신 속도(baud rate) 설정
    ser = serial.Serial('/dev/ttyArduino', 9600, timeout=1)
    time.sleep(2)  # 시리얼 연결 안정화를 위한 대기 시간

    pre_command = 'S'
    # 메인 스레드에서 TCPClientManager 인스턴스 생성
    # client_manager = TCPClientManager()
    
    # speed_client = client_manager.get_client("speed_client", data_type='str', host=HOST, port=4003)
    # speed_client.start(socket.SOCK_DGRAM)

    udp_client_manager = UDPClientManager()
    client_speed = udp_client_manager.get_client("speed", 'str', '192.168.26.136', 4003)
    client_speed.start()

    cleint_front = udp_client_manager.get_client("front", 'image', '192.168.26.136', 4000)
    cleint_front.start()

    client_lane = udp_client_manager.get_client("lane", 'image', '192.168.26.136', 4001)
    client_lane.start()


    image_thread = threading.Thread(target=send_cam_frame)
    image_thread.daemon = True
    image_thread.start()

    encoder_thread = threading.Thread(target=encoder_monitor)
    encoder_thread.daemon = True  # 메인 프로그램이 종료되면 스레드도 종료
    encoder_thread.start()


    upd_manager = UDPServerManager()
    upd_manager.start_server(host=host, port=port,data_handler=custom_data_handler)


    # error_server = TCPServerManager()
    print("hi")
    # tcp_server_manager = TCPServerManager()
    # error_server.start_server(host=host, port=4006, data_handler=handle_receive_tcp_data)

    # # GET 요청을 주기적으로 보내는 스레드 실행
    # fetch_thread = threading.Thread(target=fetch_commands)
    # fetch_thread.daemon = True
    # fetch_thread.start()

    #TCP_server_열기 명령 받는 작업
    

    # 메인 스레드는 다른 작업을 수행할 수 있으나, 현재는 대기 상태로 두어야 합니다.
    try:
        while True:
            time.sleep(1)  # 메인 스레드는 계속 실행되도록 대기
    except KeyboardInterrupt:
        print("프로그램 종료")  # Ctrl+C로 종료
    finally:
        motor_stop()
        ser.close()
        lane_cam.release()
        front_cam.release()
        upd_manager.stop_server()
        udp_client_manager.stop_all_clients()




    # 차선 데이터 전송 예제 코드
    # lane_data = {
    #     "lane_position": 10,
    #     "lane_curvature": 0.001
    # }
    # command_data= "F30"
    # client.send_data(f"http://localhost:{clients['Service']}", "robot", {"data": command_data})


    # 1. Json으로 만들기
    """
        lane_data = {
        "lane_position": random.uniform(-1.0, 1.0),
        "lane_curvature": random.uniform(0, 0.001)
    }
    """

    # 2. Service에 데이터 전송하기
    """
        client.send_data(f"http://localhost:{clients['Service']}", {"data": lane_data})
    """

    # 3. 터미널에서 실행
    # 아래의 경로에서 터미널에 실행하면 main.py 2개가 각각의 터미널에서 실행됨.
    ## (yolo) mr@mr:~/dev_ws/deeplearning-repo-3$ 
    """
gnome-terminal -- bash -c "python3 Intelligence_Vehicle_Service/Main.py; exec bash" & gnome-terminal -- bash -c "python3 Intelligence_Vehicle_AI/Perception/Lane/Main.py; exec bash"
    """

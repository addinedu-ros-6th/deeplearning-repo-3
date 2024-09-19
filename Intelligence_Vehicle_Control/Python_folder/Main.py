import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
import time

clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004,
    "Robot":5005
}

if __name__ == "__main__":
    service = IVService()
    client = FlaskClient(client_id="Robot", port= clients["Robot"])
    client.set_callback(service.handle_receive_http_data)

    while True:
        if client.is_port_open(host='localhost', port=clients["Service"]):
            break
        print("Waiting for a server response.")
        time.sleep(1)
    
    import requests
    import serial
    import time
    import threading

    # 아두이노가 연결된 시리얼 포트와 통신 속도(baud rate) 설정
    ser = serial.Serial('/dev/ttyArduino', 9600, timeout=1)
    time.sleep(2)  # 시리얼 연결 안정화를 위한 대기 시간

    pre_command = 'S'

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
        encoder_url = 'http://192.168.0.12:4100/post_encoder'
        pre_encoder_value =0
        while True:
            encoder_value = read_encoder()
            
            if encoder_value:

                parts = encoder_value.split()
                
                # "L:" 뒤의 값을 가져와서 int로 변환
                L_encoder = int(parts[2].replace('L:', ''))
                
                # "R:" 뒤의 값을 가져와서 int로 변환
                R_encoder = int(parts[3].replace('R:', ''))

                mean_encoder_value = (abs(L_encoder)+abs(R_encoder))/2
                
                delta_encoder = mean_encoder_value-pre_encoder_value
                cur_speed = delta_encoder*20.42/2500

                print(f"현재 속도: {cur_speed}")
                speed_data ={"encoder":cur_speed}
                # encoder_data =str(encoder_value)
                speed_response = requests.post(encoder_url,json=speed_data)
                print(cur_speed)
                print(speed_data)
                print(speed_response.status_code)
                print(speed_response.json())

                pre_encoder_value = mean_encoder_value
            time.sleep(0.1)  # 0.1초마다 엔코더 값 읽기

    def fetch_commands():
        global pre_command
        command_error_flag =True
        while True:
            if command_error_flag == True:
                url = 'http://192.168.0.12:4100/get_command'
            else:
                url = 'http://192.168.0.12:4100/get_error'
            try:
                response = requests.get(url)
                command = response.text.strip()  # 명령을 문자열로 읽음
                print(f"GET 요청 응답: {response.status_code}")
                print(f"응답 본문: {command}")

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

    # 엔코더 모니터링을 위한 스레드 실행
    encoder_thread = threading.Thread(target=encoder_monitor)
    encoder_thread.daemon = True  # 메인 프로그램이 종료되면 스레드도 종료
    encoder_thread.start()

    # GET 요청을 주기적으로 보내는 스레드 실행
    fetch_thread = threading.Thread(target=fetch_commands)
    fetch_thread.daemon = True
    fetch_thread.start()

    # 메인 스레드는 다른 작업을 수행할 수 있으나, 현재는 대기 상태로 두어야 합니다.
    try:
        while True:
            time.sleep(1)  # 메인 스레드는 계속 실행되도록 대기
    except KeyboardInterrupt:
        print("프로그램 종료")  # Ctrl+C로 종료
    finally:
        motor_stop()
        ser.close()




    # 차선 데이터 전송 예제 코드
    # lane_data = {
    #     "lane_position": 10,
    #     "lane_curvature": 0.001
    # }
    command_data= "F30"
    client.send_data(f"http://localhost:{clients['Service']}", "robot", {"data": command_data})


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

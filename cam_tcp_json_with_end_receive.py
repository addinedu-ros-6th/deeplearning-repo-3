import socket
import json
import base64
import numpy as np
import cv2

def display_image_from_json(json_data):
    try:
        # 수신된 데이터가 비어있거나 유효하지 않은 경우를 처리
        if not json_data:
            print("Received empty data")
            return

        # JSON 데이터 파싱
        data = json.loads(json_data)

        if data['type'] == 'image' and data['image']:
            # Base64로 인코딩된 이미지 데이터를 복원
            image_data = base64.b64decode(data['image'])
            np_arr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow(f'Camera {data["index"]}', img)
                cv2.waitKey(1)
        else:
            print(f"Invalid image data: {data}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error displaying image: {e}")

def receive_data_from_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    buffer = ""
    
    try:
        while True:
            # 데이터 수신
            data = client_socket.recv(4096).decode('utf-8')
            
            if not data:
                break
            
            # 수신한 데이터를 버퍼에 추가
            buffer += data
            
            # 구분자인 '\n'을 기준으로 메시지 분리
            while '\n' in buffer:
                # '\n' 기준으로 한 줄씩 처리
                line, buffer = buffer.split('\n', 1)
                if line:
                    display_image_from_json(line)
    finally:
        client_socket.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    receive_data_from_server('192.168.0.11', 4002)
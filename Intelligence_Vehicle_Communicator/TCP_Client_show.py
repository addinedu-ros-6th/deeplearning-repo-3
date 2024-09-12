import socket
import numpy as np
import cv2

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# HOST = '192.168.0.24'
HOST = '172.20.10.5'
PORT = 4002

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 카메라 인덱스 설정
camera1_index = 0
camera2_index = 1

try:
    while True:
        # 첫 번째 카메라 인덱스 전송
        client_socket.send(str(camera1_index).encode())
        
        length1 = recvall(client_socket, 16)
        if length1 is None:
            break
        
        length1 = int(length1)
        if length1 == 0:
            continue
        
        stringData1 = recvall(client_socket, length1)
        if stringData1 is None:
            break
        
        data1 = np.frombuffer(stringData1, dtype='uint8')
        decimg1 = cv2.imdecode(data1, 1)

        # 두 번째 카메라 인덱스 전송
        client_socket.send(str(camera2_index).encode())
        
        length2 = recvall(client_socket, 16)
        if length2 is None:
            break
        
        length2 = int(length2)
        if length2 == 0:
            continue
        
        stringData2 = recvall(client_socket, length2)
        if stringData2 is None:
            break
        
        data2 = np.frombuffer(stringData2, dtype='uint8')
        decimg2 = cv2.imdecode(data2, 1)

        # 화면에 프레임 표시
        cv2.imshow('Camera 1', decimg1)
        cv2.imshow('Camera 2', decimg2)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    client_socket.close()
    cv2.destroyAllWindows()

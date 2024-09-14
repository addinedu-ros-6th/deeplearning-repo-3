import socket
import threading
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPNewVersion import TCPConnection
import threading


def handle_client(client_socket, client_address):
    tcp_connection = TCPConnection()
    tcp_connection.conn = client_socket
    print(f"클라이언트 {client_address} 연결됨")

    while True:
        try:
            image_data = tcp_connection.receive_data()
            if image_data is None:
                break
            
            text_data = tcp_connection.receive_data()
            if text_data is None:
                break
            
            print(f"클라이언트 {client_address}로부터 수신:")
            print(f"이미지 크기: {image_data.shape}")
            print(f"텍스트: {text_data}")

        except Exception as e:
            print(f"클라이언트 {client_address} 처리 중 오류 발생: {e}")
            break

    print(f"클라이언트 {client_address} 연결 종료")
    client_socket.close()

def start_server(host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"서버가 {host}:{port}에서 시작되었습니다.")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
from datetime import datetime
import time
import numpy as np
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)
from Intelligence_Vehicle_Communicator.TCPNewVersion import TCPConnection
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


def create_timestamped_image(width=640, height=480):
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    font = ImageFont.load_default()
    draw.text((10, 10), current_time, fill='white')
    return np.array(image)

def show_image(image):
    plt.imshow(image)
    plt.axis('off')
    plt.show(block=False)
    plt.pause(0.1)

def run_client(client_id, host='localhost', port=12345):
    tcp_connection = TCPConnection(host, port)
    tcp_connection.connect_to_server()

    frame_count = 0
    try:
        while True:
            image = create_timestamped_image()
            show_image(image)
            text = f"Client {client_id} - Frame {frame_count}"

            tcp_connection.send_data(image, 'image')
            tcp_connection.send_data(text, 'str')

            print(f"Client {client_id} sent frame {frame_count}")
            frame_count += 1
            time.sleep(1/30)

    except KeyboardInterrupt:
        print(f"Client {client_id} 종료")
    finally:
        tcp_connection.close()
        plt.close('all')

if __name__ == "__main__":
    import multiprocessing

    client1 = multiprocessing.Process(target=run_client, args=(1,))
    client2 = multiprocessing.Process(target=run_client, args=(2,))

    client1.start()
    client2.start()

    client1.join()
    client2.join()
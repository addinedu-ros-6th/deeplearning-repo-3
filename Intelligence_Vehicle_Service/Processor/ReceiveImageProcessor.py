import sys
import os
from typing import Callable
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)

from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClient, TCPClientManager
from Intelligence_Vehicle_Service.Processor.Processor import Processor
import numpy as np
import json

class ReceiveImageProcessor(Processor):

    def set_send_image_callback(self, callback):
        self.sendCallback = callback


    def execute(self, data):
        print(data)
        

    


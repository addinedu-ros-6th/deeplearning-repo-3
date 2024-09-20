import base64
import pickle
import sys
import os

import cv2
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor, ProcessorMeta
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np


class GUIViewerProcessor(QObject, Processor, metaclass=ProcessorMeta):
    frontView = pyqtSignal(np.ndarray)
    laneView = pyqtSignal(np.ndarray)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def execute(self, data):
        key_list = list(data.keys())
        print("키 리스트: ", key_list)

        image_type = data['data']['type']
        print('\033[38;2;77;5;108m'+'image_type: ' + '\033[38;2;20;121;218m', image_type, '\033[0m')
        encoded_image = data['data']['image']
        
        print(f"Encoded image data (first 100 chars): {encoded_image[:100]}")
        
        try:
            # Base64 디코딩
            image_bytes = base64.b64decode(encoded_image)
            
            # numpy 배열로 변환
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # 이미지 디코딩
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            print(f"Decoded image shape: {image.shape}")
            
        except Exception as e:
            print(f"\033[93mError decoding image: {e}\033[0m")
            import traceback
            traceback.print_exc()
            return

        if image_type == 'front':
            self.frontView.emit(image)
        elif image_type == 'lane':
            self.laneView.emit(image)

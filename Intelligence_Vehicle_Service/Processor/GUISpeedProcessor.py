import base64
import sys
import os

import cv2
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor, ProcessorMeta
from PyQt5.QtCore import QObject, pyqtSignal
from Custom_print  import custom_print

class GUISpeedProcessor(QObject, Processor, metaclass=ProcessorMeta):
    hudSignal = pyqtSignal(str)

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def execute(self, data):
        print(f"GUISpeedProcessor: {data}")
        self.hudSignal.emit(data['data'])



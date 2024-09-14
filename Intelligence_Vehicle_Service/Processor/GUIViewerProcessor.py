import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np

class GUIViewerProcessor(Processor, QObject):
    frontView = pyqtSignal(np.ndarray)
    laneView = pyqtSignal(np.ndarray)

    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)

    def execute(self, data):
        key_list = list(data.keys())
        print(key_list)

        # front이면 
        # self.frontView.emit(여기에 이미지)
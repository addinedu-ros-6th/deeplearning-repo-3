import sys
import os
# 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time
import cv2
import numpy as np
from Observer import *
from Intelligence_Vehicle_AI.Perception.Object.obstacleDetector import Train



class BlinkThread(QThread):
    blink_signal = pyqtSignal(bool)

    def __init__(self, sec, count, signal):
        super().__init__()
        self.sec = sec
        self.blink_signal.connect(signal)
        self.count = count

    def run(self):
        for _ in range(self.count):
            if self.isInterruptionRequested():
                return
            self.blink_signal.emit(True)
            self.msleep(1000)
            if self.isInterruptionRequested():
                return
            self.blink_signal.emit(False)
            self.msleep(1000)
    
    def stop(self):
        self.requestInterruption()
        self.wait()  # 스레드가 완전히 종료될 때까지 대기

from_class = uic.loadUiType("Intelligence_Vehicle_GUI/ui/main.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, parent=None):
        super(WindowClass, self).__init__(parent)
        self.setupUi(self)
        # self.label_system_message.hide()

        # self.label_system_message.setVisible(False)
        # self.label_system_message.setText("test")
        # self.frontViewer = Thread(1, self.update_viewer)
        self.frontCameraPixmap = QPixmap()
        self.laneCameraPixmap = QPixmap()
        self.mutex = QMutex() 

    def start_blink_system_message(self, text):
        self.label_system_message.setText(text)
        print("System Message는 구현 중입니다.")

        # if self.blink_thread and self.blink_thread.isRunning():
        #     self.blink_thread.stop()
        #     self.blink_thread.wait()

        # self.blink_thread = BlinkThread(0.3, 3, self.blink_handler_system_message)
        # self.blink_thread.start()
        
    def blink_handler_system_message(self, isActive):
        self.label_system_message.setVisible(isActive)

    def update_front_view(self, image):
        self.update_camera_view(self.label_front_view, image, self.frontCameraPixmap)

    def update_lane_view(self, image):
        self.update_camera_view(self.label_lane_view, image, self.laneCameraPixmap)

    def update_camera_view(self, view:QLabel, image:np.ndarray, pixmap:QPixmap):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
        pixmap = pixmap.fromImage(qimage)
        pixmap = pixmap.scaled(view.width(), view.height())
        view.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()

    train = Train()
    train.front_viewer.connect(myWindow.update_front_view)
    train.addEvent("dog", DetectDog(myWindow.start_blink_system_message))
    train.addEvent("dog_cancel", DetectDogCancel(myWindow.start_blink_system_message))
    train.addEvent("child", DetectChildZone(myWindow.start_blink_system_message))
    train.addEvent("child_deactive", DetectChildCancellation(myWindow.start_blink_system_message))
    train.addEvent("Red_sign", DetectTrafficLightRed(myWindow.start_blink_system_message))
    train.addEvent("Blue_sign",  DetectTrafficLightBlue(myWindow.start_blink_system_message))
    train.addEvent("person", DetectPerson(myWindow.start_blink_system_message))
    train.addEvent("person_cancel", DetectPersonCancel(myWindow.start_blink_system_message))
    train.addEvent("50km", DetectSpeedLimitSign(myWindow.start_blink_system_message))
    train.addEvent("50km_deactive", DetectSpeedCancellation(myWindow.start_blink_system_message))
    train.addEvent("stop", DetectStop(myWindow.start_blink_system_message))
    train.addEvent("stop_cancel", DetectStopCancel(myWindow.start_blink_system_message))
    train.run()

    sys.exit(app.exec_())
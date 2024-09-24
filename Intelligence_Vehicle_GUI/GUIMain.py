import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from Intelligence_Vehicle_GUI.MainWindow import MainWindow 

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet
clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004,
    "GUI": 5005
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    apply_stylesheet(app, theme='dark_amber.xml')
    myWindow.show()

    service = IVService()
    service.register_gui_processor(myWindow)

    client = FlaskClient(client_id="GUI", port= clients["GUI"])
    client.set_callback(service.handle_receive_http_data)

    sys.exit(app.exec_())
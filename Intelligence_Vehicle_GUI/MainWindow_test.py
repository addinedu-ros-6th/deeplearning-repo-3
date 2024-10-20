import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '..')  # 상위 폴더로 이동
sys.path.append(relative_path)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ultralytics import YOLO
import mysql.connector
import numpy as np
from PyQt5 import uic
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import datetime
import mplcursors
from datetime import datetime
import pandas as pd
import matplotlib.dates as mdates
from Intelligence_Vehicle_ETC.DBmanager import MySQLConnection
import math
from qt_material import apply_stylesheet
import cv2
class Camera(QThread):
    update = pyqtSignal()

    def __init__(self,sec=0.1, parent = None):
        super().__init__()
        self.main = parent
        self.running = True
    
    def run(self):
        count = 0 
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)
    
    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./Intelligence_Vehicle_GUI/ui/main.ui", self)


        self.setWindowTitle("IV GUI")
        self.label = QLabel(self)

        self.frontCameraPixmap = QPixmap()
        self.laneCameraPixmap = QPixmap()
        
        self.signpixmap = QPixmap()
        self.obstaclepixmap = QPixmap()

        self.camera = Camera(self)
        self.camera.running = False
        self.pixmap = QPixmap()


        self.model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
        self.dbm = MySQLConnection.getInstance()
        self.dbm.db_connect("172.20.10.6", 3306, "deep_project", "yhc", "1234")

        self.pushButton_camera.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)

        self.obstacleFlag = False
        self.signsFlag =False
        #log tab

        self.pushButton_search.clicked.connect(self.print_driving)
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setDateTime(QDateTime.currentDateTime()) 
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.graph_widget = PlotWidget()

        layout = QVBoxLayout(self.widget_chart)  # QLabel에 레이아웃 설정
        layout.addWidget(self.graph_widget.canvas)


    def updateCamera(self):
        retval,frame= self.video.read()

        results = self.model.track(frame, conf=0.3, imgsz=480,verbose=False)
        if retval:
            image = cv2.cvtColor(results[0].plot(), cv2.COLOR_BGR2RGB)
            h,w,c = image.shape
            qimage = QImage(image.data, w,h,w*c, QImage.Format_RGB888)
            self.pixmap= self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label_Obstacle_Camera.width(),self.label_Obstacle_Camera.height())
            self.label_Obstacle_Camera.setPixmap(self.pixmap)

        self.track_ids = results[0].boxes.cls.int().cpu().tolist()
       
        self.printObstacleImage()
        self.printSpeedImage()
    
    def printObstacleImage(self):
        self.pixmap = QPixmap()
        for i in self.track_ids:
            if(i ==1):
                self.obstaclepixmap.load("./Intelligence_Vehicle_GUI/ui/image/red_sign.jpg")
                self.label_blinker.setScaledContents(True)
                self.label_blinker.setPixmap(self.obstaclepixmap)  
            elif(i==4):
                self.obstaclepixmap.load("./Intelligence_Vehicle_GUI/ui/image/blue_sign.jpg")
                self.label_blinker.setScaledContents(True)
                self.label_blinker.setPixmap(self.obstaclepixmap) 

    def printSpeedImage(self):
        for i in self.track_ids:
            if(i ==0):
                self.pixmap2.load("./Intelligence_Vehicle_GUI/ui/image/child_clear.jpg")
                self.label_child_sign.setScaledContents(True)
                self.label_child_sign.setPixmap(self.pixmap2)
            elif(i==3):
                if(self.signsFlag ==False):
                    self.dbm.set_eventlog("signs", "ChildZone")
                    self.signsFlag  = True    
                self.signpixmap.load("./Intelligence_Vehicle_GUI/ui/image/child.jpg")
                self.label_child_sign.setScaledContents(True)
                self.label_child_sign.setPixmap(self.signpixmap)
            elif(i==7):
                if(self.signsFlag ==False):
                    self.dbm.set_eventlog("signs", "SpeedLimit50")
                    self.signsFlag = True    
                self.signpixmap.load("./Intelligence_Vehicle_GUI/ui/image/50speed.jpg")
                self.label_speed_sign.setScaledContents(True)
                self.label_speed_sign.setPixmap(self.signpixmap)
            elif(i==2):
                if(self.obstacleFlag ==False):
                    print("insert compledte")
                    self.dbm.set_eventlog("obstacle", "WildAnimal")
                    self.obstacleFlag = True           
                self.obstaclepixmap.load("./Intelligence_Vehicle_GUI/ui/image/dog.png")
                self.label_obstacle.setScaledContents(True)
                self.label_obstacle.setPixmap(self.obstaclepixmap) 
            else:
                self.label_speed_sign.clear()
                self.label_child_sign.clear()
                self.obstacleFlag = False   
          

    def clickCamera(self):
         if self.camera.running  == False:
             self.isCameraOn = True
             self.cameraStart()
         else:
             self.isCameraOn = False
             self.cameraStop()
    def cameraStart(self):
         # if self.playvideo.running == True:
         #     self.mp4Stop()
         self.camera.running = True
         self.camera.start()
         self.video = cv2.VideoCapture(-1)
    def cameraStop(self):
         self.camera.running = False
         self.count = 0
         self.video.release()
         self.label_camera.clear()


    def print_speed(self, speed):
        print(speed)
        self.dbm.set_drivinglog(speed)
        self.lcdNumber_speed.display(speed)

    
    def print_driving(self):
        selected_start_time = self.dte_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        selected_end_time = self.dte_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        sql_results = self.dbm.get_obstacle_by_time(selected_start_time,selected_end_time)

        self.tableWidget.setRowCount(0)
        if(len(sql_results)!=0):
            for value in sql_results:
                print(value)  
                row  = self.tableWidget.rowCount() 
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(value[0])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(value[1])))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(value[2])))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(value[3])))

        self.graph_widget.plot(sql_results)
        #occurtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #self.dbm.set_eventlog("obstacle", "person")

    def closeEvent(self, event):
            # 윈도우 종료 시 데이터베이스 연결 종료
        self.dbm.disconnection()
        event.accept()

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 그래프를 그릴 Figure 객체 생성
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self,plot_results):
        self.figure.clear()
    
        x = np.array([value[3] for value in plot_results])
        y = np.array([value[0] for value in plot_results]).astype(int)
        obs = np.array([value[1] for value in plot_results])
        type = np.array([value[2] for value in plot_results])
        
        # 그래프 그리기
        ax = self.figure.add_subplot(111)  # 1x1 그리드의 첫 번째 서브플롯
        
        line, =ax.plot(x, y, label="IV")
    
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        #ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))    
        mpl=mplcursors.cursor(line, hover=True)

        @mpl.connect("add")
        def on_add(sel):
            
            serial_value = np.float64(sel.target[0])  # 예시 날짜 시리얼
            
            index = sel.index
            decimal_part = index - int(index)
           
            if(decimal_part >0.98):
               index=  math.ceil(index)
            else:
                index=  round(index)   
            
            # 변환
            date_time = pd.to_datetime('1970-01-01') + pd.to_timedelta(serial_value, unit='D')
            time_value = date_time.strftime('%Y-%m-%d %H:%M:%S')
            
            sel.annotation.set(text=f'time: {time_value}\nSpeed: {sel.target[1]}\n obstacle : {obs[index]}\n type : {type[index]}',
                       fontsize=12,
                       bbox=dict(facecolor='lightyellow', alpha=0.8))

        threshold = ["obstacle","signs"]   # 임계값

        for i in range(len(y)):
            if obs[i] in threshold:  # 조건: y 값이 임계값을 초과할 때
                
                ax.plot(x[i], y[i], marker='o', markersize=7, color='blue')
                          
        ax.set_title("speed record")
        ax.set_xlabel("time")
        ax.set_ylabel('speed')

        ax.legend()
        self.canvas.draw()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    # apply_stylesheet(app, theme='dark_amber.xml')

    window.show()

    sys.exit(app.exec_())
#['dark_amber.xml', 
#'dark_blue.xml', 
#'dark_cyan.xml', 
#'dark_lightgreen.xml', 
#'dark_medical.xml', 
#'dark_pink.xml', 
#'dark_purple.xml',
#'dark_red.xml', 
#'dark_teal.xml',
#'dark_yellow.xml',
#'light_amber.xml', 
#'light_blue.xml', 
#'light_blue_500.xml', 
#'light_cyan.xml', 
#'light_cyan_500.xml', 
#'light_lightgreen.xml', 
#'light_lightgreen_500.xml', 
#'light_orange.xml', 
#'light_pink.xml', 
#'light_pink_500.xml',
#'light_purple.xml', 
#'light_purple_500.xml', 
#'light_red.xml', 
#'light_red_500.xml',
#'light_teal.xml', 
#'light_teal_500.xml', 
#'light_yellow.xml']

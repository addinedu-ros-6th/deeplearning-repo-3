
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
#from Intelligence_Vehicle_AI.Perception.Object.ObstacleDetector import ObstacleDetector
import numpy as np
from Observer import *
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

class Speed(QThread):
    update = pyqtSignal()

    def __init__(self,sec=0.1, parent = None):
        super().__init__()
        self.main = parent
        self.running = True
        
    def run(self):
        count = 0 
        while self.running == True:
            self.update.emit()
            time.sleep(1)
    
    def stop(self):
        self.running = False        

#ui 파일 연결 - 코드 파일과 같은 폴더내에 위치해야함
from_class = uic.loadUiType("./Intelligence_Vehicle_GUI/ui/main.ui")[0]
from_class2 = uic.loadUiType("./Intelligence_Vehicle_GUI/ui/log_window.ui")[0]
class SecondWindow(QMainWindow,from_class2):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Log Page")
       
        self.dbm = MySQLConnection.getInstance()
        
        self.dbm.db_connect("192.168.0.130",3306, "deep_project", "yhc", "1234")
        
        self.pushButton_search.clicked.connect(self.print_driving)

        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setDateTime(QDateTime.currentDateTime()) 

        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)


        # PlotWidget 추가
        self.graph_widget = PlotWidget()
        layout = QVBoxLayout(self.widget_chart)  # QLabel에 레이아웃 설정
        layout.addWidget(self.graph_widget.canvas)
        

    def select_data(self, table, columns= ("*",), where = None, order = None, join = None,limit=20):
        columns_str = ', '.join(columns)

        sql = f"""
          SELECT {columns_str}
          FROM {table}
        """
        if join:
          sql += f" {join}" 

        if where:
          sql += f" WHERE {where}"

        if order:
          sql += f" ORDER BY {order}"
        if limit:
          sql += f" LIMIT {limit}"

        print("select_data: ", sql)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results


    def print_driving(self):

        selected_start_time = self.dte_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        selected_end_time = self.dte_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        #sql_results=self.select_data("DrivingLog",where="time >'"+selected_start_time+"' and "+"time <'"+selected_end_time+"'")
        #sql_results=self.select_data("EventLog",columns=("COALESCE(CAST(DrivingLog.speed AS SIGNED), 'N/A') AS speed","COALESCE(EventLog.category,'N/A')AS category",  "COALESCE(EventLog.type, 'N/A') AS type",  "DrivingLog.time" ),
        #                             join="RIGHT JOIN DrivingLog ON DrivingLog.time = EventLog.occurtime",
        #                             where="time >'"+selected_start_time+"' and "+"time <'"+selected_end_time+"'")
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
   


    def closeEvent(self, event):
            # 윈도우 종료 시 데이터베이스 연결 종료
        self.dbm.disconnection()
               
        event.accept()

    def open_second_window(self):
        self.second_window = SecondWindow()  # 두 번째 윈도우 객체 생성
        self.second_window.show()  # 두 번째 윈도우 표시
        self.close()  # 현재 윈도우 닫기



   #def open_first_window(self):
   #    self.first_window = WindowClass()  # 첫 번째 윈도우 객체 생성
   #    self.first_window.show()  # 첫 번째 윈도우 표시
   #    self.close()  # 현재 윈도우 닫기



class WindowClass(QMainWindow, from_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
       
        self.setWindowTitle("Test10")
        self.label = QLabel(self)

        self.current_number=0
        self.speed = Speed(self)
        self.speed.start()

        self.frontCameraPixmap = QPixmap()
        self.laneCameraPixmap = QPixmap()
        
        self.camera = Camera(self)
        self.camera.running = False
        self.pixmap = QPixmap()
        self.model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")

        self.pushButton_camera.clicked.connect(self.clickCamera)
        self.pushButton_log.clicked.connect(self.open_second_window)

        self.camera.update.connect(self.updateCamera)
        self.speed.update.connect(self.speed_update)
    
    def open_second_window(self):
        self.second_window = SecondWindow()  # 두 번째 윈도우 객체 생성
        self.second_window.show()  # 두 번째 윈도우 표시
        #self.close()  # 현재 윈도우 닫기

    def update_front_view(self, image):
        self.update_camera_view(self.label_Obstacle_Camera, image, self.frontCameraPixmap)

    def update_lane_view(self, image):
        self.update_camera_view(self.label_Lane_Camera, image, self.laneCameraPixmap)

    def update_camera_view(self, view:QLabel, image:np.ndarray, pixmap:QPixmap):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
        pixmap = pixmap.fromImage(qimage)
        pixmap = pixmap.scaled(view.width(), view.height())
        view.setPixmap(pixmap)

        # self.track_ids = results[0].boxes.cls.int().cpu().tolist()
        # print(self.track_ids)
        # self.printObstacleImage()
        # self.printSpeedImage() 


    def updateCamera(self):
    # self.label.setText('Camera Running : ' + str(self.count))
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
        print(self.track_ids)
        self.printObstacleImage()
        self.printSpeedImage() 
                        
    def printObstacleImage(self):
        self.pixmap = QPixmap()
        for i in self.track_ids:

            if(i==2):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/dog.png")
            elif(i==5):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/stop.png")
            elif(i ==6):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/person.png")
            else:
                self.label_obstacle.clear()
                
        self.label_obstacle.setScaledContents(True)
        self.label_obstacle.setPixmap(self.pixmap)

    def printSpeedImage(self):
        self.pixmap = QPixmap()
        for i in self.track_ids:
            if(i ==0):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/child_clear.jpg")
                self.label_child_sign.setScaledContents(True)
                self.label_child_sign.setPixmap(self.pixmap)
            elif(i==3):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/child.jpg")
                self.label_child_sign.setScaledContents(True)
                self.label_child_sign.setPixmap(self.pixmap)
            elif(i==7):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/50speed.jpg")
                self.label_speed_sign.setScaledContents(True)
                self.label_speed_sign.setPixmap(self.pixmap)
            elif(i==8):
                self.pixmap.load("./Intelligence_Vehicle_GUI/ui/image/50speed_clear.jpg")
                self.label_speed_sign.setScaledContents(True)
                self.label_speed_sign.setPixmap(self.pixmap)
            else:
                self.label_speed_sign.clear()
                self.label_child_sign.clear()


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

    def speed_update(self):

        self.current_number += 1  # 숫자 증가
        self.lcdNumber_speed.display(self.current_number)

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

        # 그래프 그리기
        #self.plot(cursor)

    def plot(self,plot_results):
        # 랜덤 데이터 생성
        #plot_results=cursor.select_data("DrivingLog",columns=("speed", "time"))
        plt.rcParams['font.family'] = 'Malgun Gothic'

        x = np.array([value[3] for value in plot_results])
        y = np.array([value[0] for value in plot_results]).astype(int)
        obs = np.array([value[1] for value in plot_results])

        # 그래프 그리기
        ax = self.figure.add_subplot(111)  # 1x1 그리드의 첫 번째 서브플롯
        
        #fig, ax = self.figure.subplots()
        line, =ax.plot(x, y, label="Ferrari")
        mpl=mplcursors.cursor(line, hover=True)
       

        @mpl.connect("add")
        def on_add(sel): 
            
            serial_value = np.float64(sel.target[0])  # 예시 날짜 시리얼

            index = sel.index
            decimal_part = index - int(index)
            if(decimal_part >0.9):
               index=  math.ceil(index)
            else:
                index=  round(index)   
            
               
            # 변환
            date_time = pd.to_datetime('1970-01-01') + pd.to_timedelta(serial_value, unit='D')
            time_value = date_time.strftime('%Y-%m-%d %H:%M:%S')
            print(index)
            sel.annotation.set(text=f'time: {time_value}\nSpeed: {sel.target[1]}\n obstacle : {obs[index]}',
                       fontsize=12,
                       bbox=dict(facecolor='lightyellow', alpha=0.8))
        
        threshold = ["장애물","표지판"]   # 임계값
        for i in range(len(y)):
            
            if obs[i] in threshold:  # 조건: y 값이 임계값을 초과할 때
                ax.plot(x[i], y[i], marker='o', markersize=8, color='blue')  # 마커 추가

                
        ax.set_title("speed record")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        #plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax.set_xlabel("time")
        ax.set_ylabel('speed')

        ax.legend()

        # 캔버스에 그린 내용을 업데이트
        self.canvas.draw()
        
  

if __name__ == "__main__":
    app = QApplication(sys.argv) #프로그램 실행
    myWindows = WindowClass() # 화면 클래스 생성
    myWindows.show() # 프로그램 화면 보이기

    sys.exit(app.exec_()) # 프로그램을 종료까지 동작시킴        


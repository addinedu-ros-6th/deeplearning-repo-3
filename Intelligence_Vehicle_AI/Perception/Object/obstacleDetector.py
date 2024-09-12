import cv2
import numpy as np
import sys
import time
from ultralytics import YOLO
from Intelligence_Vehicle_GUI.Observer import * 
from PyQt5.QtCore import QObject, pyqtSignal

# 객체를 관리할 클래스를 정의
class DetectedObject:
    def __init__(self, detection_time, width, height):
        self.detection_time = detection_time  # 검출 시간
        self.width = width  # bounding box 너비
        self.height = height  # bounding box 높이

    def __str__(self):
        return f"Detected at: {self.detection_time}, Width: {round(self.width,2)}, \
Height: {round(self.height,2)}"

class ObjectAlertManager:
    def __init__(self, alert_interval = 10, min_detections = 3, width_threshold = (50, 300)):
        self.alert_interval = alert_interval # 알림 제한 시간 (초)
        self.min_detections = min_detections # 최소 검출 횟수
        self.width_threshold = width_threshold # 너비 기준 (min, max)
        self.last_alert_times = {} # 각 객체에 대해 마지막으로 알림을 준 시간
        self.detection_counts = {}  # 각 객체별 검출 횟수
    
    def should_alert(self, obj_name, width):
        curr_time = time.time()
        # 알림 제한 시간 체크
        if obj_name in self.last_alert_times:
            time_since_last_alert = curr_time - self.last_alert_times[obj_name]
            if time_since_last_alert < self.alert_interval:
                return False
        # 검출 횟수 업데이트
        if obj_name not in self.detection_counts: self.detection_counts[obj_name] = 1
        else: self.detection_counts[obj_name] += 1
        # 검출 횟수가 일정 기준 이상이 되고 너비가 설정된 범위를 벗어나면 알림

        if self.detection_counts[obj_name] >= self.min_detections and (width < self.width_threshold[0] or width > self.width_threshold[1]):
            self.last_alert_times[obj_name] = curr_time  # 알림 시간 업데이트
            self.detection_counts[obj_name] = 0  # 검출 횟수 초기화
            return True

        return False
alert_manager = ObjectAlertManager(alert_interval=10, min_detections=3,width_threshold=(50, 300))

class Train(QObject, ObstacleSubject):

    front_viewer = pyqtSignal(np.ndarray)

    def __init__(self):
        QObject.__init__(self)
        ObstacleSubject.__init__(self)
        self.detected_objects = {}
        self.model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
        self.cap = cv2.VideoCapture("./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Empty video frame or completed processing")
                    break
                    
                if cv2.waitKey(1) == ord("q"):
                    break

                frame = cv2.resize(frame, (720, 480))
                self.front_viewer.emit(frame)
                results = self.model.track(frame, conf=0.3, imgsz=480,verbose=False)
                cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                
                # 검출된 객체 처리
                if results[0].boxes.id is not None:
                    for res in results:
                        for box in res.boxes:
                            res_id = box.id[0].tolist()
                            class_id = int(box.data[0][-1])
                            object_name = str(self.model.names[class_id])  # 객체 이름
                            x, y, w, h = box.xywh[0].tolist()  # bounding box 정보
                            # curr_time = time.strftime("%H:%M:%S")

                            self.detected_objects[object_name] = DetectedObject(
                                detection_time=time.strftime("%H:%M:%S"), 
                                width=w, 
                                height=h
                            )

                            if alert_manager.should_alert(object_name, w):
                                self.attach(self._detectEvents[object_name])
                                print("#############################################")
                                print('\033[91m'+f"ALERT: {object_name} detected with width {w}"+'\033[0m')
                                print("#############################################")                
                    
                # for name in self.detected_objects:
                #     print("time "+ name + " detected : ", 
                #     self.detected_objects[name].detection_time)
                #     print("width of " + name + " : ", round(self.detected_objects[name].width,2 ))
                
                # 결과를 보여줌
                cv2.imshow("Live Camera", results[0].plot())
                self.notify()
                if cv2.waitKey(1) == ord('q'):
                    break
        finally:
            self.release_resources()
        
    def release_resources(self):
        if hasattr(self, "cap"):
            self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        self.release_resources()
    
# trainer = Train()
# trainer.run()
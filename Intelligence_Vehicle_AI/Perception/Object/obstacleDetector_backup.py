import cv2
import numpy as np
import sys
import time
from ultralytics import YOLO

class DetectedObject:
    def __init__(self, detection_time, y_position):
        self.detection_time = detection_time
        self.y_position = y_position          # 객체의 y 위치
        self.detection_count = 1              # 검출된 횟수
        self.detection_status = False         # 검출 상태 (True/False)

    def update(self, detection_time, y_position):
        self.detection_time = detection_time 
        self.y_position = y_position
        self.detection_count += 1

class Train:

    def __init__(self):
        self.detected_objects = {}  # 객체 정보 저장
        self.model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
        self.cap = cv2.VideoCapture("./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")
        self.alert_threshold = 20
        self.detection_timeout = 1

    def notify(self, object_name):
        obj = self.detected_objects[object_name]
        if obj.detection_status:
            print(f"Object {object_name}: Alert ON")
        else:
            print(f"Object {object_name}: Alert OFF")

    def check_detection_timeout(self, current_time):
        for obj_name in list(self.detected_objects.keys()):
            obj = self.detected_objects[obj_name]
            if obj.detection_status and current_time > self.detection_timeout + obj.detection_time:
                obj.detection_count = 0
                obj.detection_status = False
                if obj_name in ['person', 'dog', 'stop']:
                    self.notify(obj_name)

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Empty video frame or completed processing")
                    break

                frame = cv2.resize(frame, (720, 480))
                results = self.model.track(frame, conf=0.3, imgsz=480, verbose=False)
                current_time = time.time()
        
                # 검출된 객체 처리
                if results[0].boxes.id is not None:
                    res = results[0]

                    for box in res.boxes:
                        res_id = box.id[0].tolist()
                        class_id = int(box.data[0][-1])
                        object_name = str(self.model.names[class_id])  # 객체 이름
                        x, y, w, h = box.xywh[0].tolist()  # bounding box 정보

                        if object_name not in self.detected_objects:
                            self.detected_objects[object_name] = DetectedObject(current_time, y)
                        else:
                            obj = self.detected_objects[object_name]
                            obj.update(current_time, y) 
                            
                            if object_name in ['Red_sign', 'Blue_sign']:
                                if obj.detection_count > self.alert_threshold and not obj.detection_status:
                                    obj.detection_status = True
                                    obj.detection_count = 0
                                    self.notify(object_name)
                            elif object_name in ['child_deactivate', 'child', '50km', '50km_deactivate']:
                                if obj.detection_count > self.alert_threshold and not obj.detection_status and obj.y_position > 120:
                                    obj.detection_status = True
                                    obj.detection_count = 0
                                    self.notify(object_name)
                            elif object_name in ['person', 'dog', 'stop']:
                                if obj.detection_count > self.alert_threshold and not obj.detection_status and obj.y_position > 240:
                                    obj.detection_status = True
                                    obj.detection_count = 0
                                    self.notify(object_name)

                self.check_detection_timeout(current_time)
                # 결과를 보여줌
                cv2.imshow("Live Camera", results[0].plot())

                if cv2.waitKey(1) == ord('q'):
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

trainer = Train()
trainer.run()

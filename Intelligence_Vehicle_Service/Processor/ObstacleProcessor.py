import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor
import time
import json

detected_objects = {}  # 객체 정보 저장

ALL_OBJECTS = ['child_deactive', 'Red_sign', 'dog', 'child', 'Blue_sign', 'stop', 'person', '50km', '50km_deactive']
detection_status_dict = {obj: False for obj in ALL_OBJECTS} # dictionary 형태
detection_status_list = [False] * len(ALL_OBJECTS)  # List to store status as boolean values # list 형태

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

class ObstacleProcessor(Processor):
    def __init__(self):

        self.alert_threshold = 20 #반복 검출 조건(횟수)
        self.detection_timeout = 1 #검출 해제 조건(시간)
        self.yLimit_signs = 120 #표지판 y조건
        self.yLimit_obstacle = 240 #장애물 y조건

    def check_detection_timeout(self, current_time):
        for obj_name in list(detected_objects.keys()):
            obj = detected_objects[obj_name]
            if obj.detection_status and current_time > self.detection_timeout + obj.detection_time:
                obj.detection_count = 0
                obj.detection_status = False
                # if obj_name in ['person', 'dog', 'stop']:
                #     self.notify(obj_name)

    # def notify(self, object_name):
    #     obj = detected_objects[object_name]
    #     if obj.detection_status:
    #         print(f"Object {object_name}: Alert ON")
    #     else:
    #         print(f"Object {object_name}: Alert OFF")

    def execute(self, data):
    
        current_time = time.time()
        # dList = data["obstacle_data"]["results"]
        dList = data["data"]["results"]
        dList_dict = json.loads(dList)

        if dList != "[]":
            dList_dict = json.loads(dList)
            for obj in dList_dict:
                object_name = obj["name"]  
                y = obj["box"]["y1"]

                if object_name not in detected_objects:
                    detected_objects[object_name] = DetectedObject(current_time, y)
                else:
                    obj = detected_objects[object_name]
                    obj.update(current_time, y) 
                    
                    if object_name in ['Red_sign', 'Blue_sign']:
                        if obj.detection_count > self.alert_threshold and not obj.detection_status:
                            obj.detection_status = True
                            obj.detection_count = 0
                    elif object_name in ['child_deactivate', 'child', '50km', '50km_deactivate']:
                        if obj.detection_count > self.alert_threshold and not obj.detection_status and obj.y_position > self.yLimit_signs:
                            obj.detection_status = True
                            obj.detection_count = 0
                    elif object_name in ['person', 'dog', 'stop']:
                        if obj.detection_count > self.alert_threshold and not obj.detection_status and obj.y_position > self.yLimit_obstacle:
                            obj.detection_status = True
                            obj.detection_count = 0

                self.check_detection_timeout(current_time)

                detection_status_dict[object_name] = detected_objects[object_name].detection_status # dictionary

                for i, obj_name in enumerate(ALL_OBJECTS):
                    detection_status_list[i] = detection_status_dict[obj_name] # list

        for objName in ALL_OBJECTS:
            print(objName, " : ", detection_status_dict[objName])
        # print("Detection status list:", detection_status_list)







        # if detected_objects.keys != []:
        #     for objName in detected_objects.keys():
        #         print(objName, " : ", detected_objects[objName].detection_status)


### TEST ###
# import cv2
# from ultralytics import YOLO
# import json

# model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
# cap = cv2.VideoCapture("./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")

# op = ObstacleProcessor()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Empty video frame or completed processing")
#         break

#     frame = cv2.resize(frame, (720, 480))
#     results = model.track(frame, conf=0.3, imgsz=480, verbose=False)
#     obstacle_data = {
#             "results": results[0].tojson() # results 변환
#         }
#     dList = obstacle_data["results"]
#     if dList != "[]":
#         dList_dict = json.loads(dList)
#         print("--------------")
#         for obj in dList_dict:
#             name = obj["name"]
#             print("name: " , name) 
#             y1 = obj["box"]["y1"]
#             print("y: ", y1)
#         print("--------------")
#     # print(dList)
        
# cap.release()

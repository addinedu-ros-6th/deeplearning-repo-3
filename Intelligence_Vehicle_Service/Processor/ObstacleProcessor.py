import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)
from Intelligence_Vehicle_Service.Processor.Processor import Processor
import time
import json

detected_objects = {}  # 객체 정보 저장
ALL_OBJECTS = ['child_deactive', 'Red_sign', 'dog', 'child', 'Blue_sign', 'stop', 'person', '50km', '50km_deactive'] # 전체 객체 정보
detection_status_dict = {obj: False for obj in ALL_OBJECTS} # 각각의 객체 검출 상태: dictionary 형태
REFINED_OBJECTS = ["RedSign", "ChildZone", "SpeedLimit50", "Pedestrian", "Barricade", "WildAnimal"]
toggledSigns_dict = {objType : False for objType in REFINED_OBJECTS}
toggledSigns_list = [False] * len(REFINED_OBJECTS)
prev_list = []

class DetectedObject:
    def __init__(self, detection_time, y_position):
        self.detection_time = detection_time  # 검출된 시간
        self.y_position = y_position          # 객체의 y 위치
        self.detection_count = 1              # 검출된 횟수
        self.detection_status = False         # 검출 상태 (True/False)

    def update(self, detection_time, y_position): # 객체 정보 업데이트 메소드
        self.detection_time = detection_time 
        self.y_position = y_position
        self.detection_count += 1

class ObstacleProcessor(Processor):
    def __init__(self):
        self.alert_threshold = 20 #반복 검출 조건(횟수)
        self.detection_timeout = 1 #검출 해제 조건(시간)
        self.yLimit_signs = 120 #표지판 y조건
        self.yLimit_obstacle = 240 #장애물 y조건

    def check_detection_timeout(self, current_time): # 검출 시간이 초과되었는지 확인하고 객체의 상태를 업데이트하는 메소드
        for obj_name in list(detected_objects.keys()):
            obj = detected_objects[obj_name]
            # 현재 시간이 검출 해제 시간보다 크면 객체의 검출 상태를 해제하고 검출 횟수를 초기화
            if obj.detection_status and current_time > self.detection_timeout + obj.detection_time: 
                obj.detection_count = 0
                obj.detection_status = False

    def execute(self, data):

        current_time = time.time()
        dList = data["results"]

        if dList != "[]":
            dList_dict = json.loads(dList) # JSON 문자열을 딕셔너리로 변환
            for obj in dList_dict:
                object_name = obj["name"]  
                y = obj["box"]["y1"]

                if object_name not in detected_objects:    # 객체가 처음 검출된 경우
                    detected_objects[object_name] = DetectedObject(current_time, y)
                else:   # 기존에 검출되었던 객체인 경우
                    obj = detected_objects[object_name]
                    obj.update(current_time, y) 
                    
                    # 객체에 따라 알림 조건을 확인하고 상태를 업데이트
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
                # dictionary of entire objects
                detection_status_dict[object_name] = detected_objects[object_name].detection_status

        self.check_detection_timeout(current_time) # 검출 시간 초과 여부 확인

        prev_list = toggledSigns_list.copy()

        if "Red_sign" in detected_objects:
            if "Blue_sign" in detected_objects:
                if (detected_objects["Red_sign"].detection_time > detected_objects["Blue_sign"].detection_time
                    and detected_objects["Red_sign"].detection_status == True):
                    toggledSigns_dict["RedSign"] = True
                else: toggledSigns_dict["RedSign"] = False
            else: toggledSigns_dict["RedSign"] = True
        elif "Red_sign" not in detected_objects and "Blue_sign" in detected_objects:
            toggledSigns_dict["RedSign"] = False

        # toggledSigns_dict["RedSign"] = detection_status_dict["Red_sign"]
        toggledSigns_dict["ChildZone"] = detection_status_dict["child"]
        toggledSigns_dict["SpeedLimit50"] = detection_status_dict["50km"]
        toggledSigns_dict["Pedestrian"] = detection_status_dict["person"]
        toggledSigns_dict["Barricade"] = detection_status_dict["stop"]
        toggledSigns_dict["WildAnimal"] = detection_status_dict["dog"]

        # update list
        for i, obj_name in enumerate(REFINED_OBJECTS):
            toggledSigns_list[i] = toggledSigns_dict[obj_name]
        # compare present list with previous list, print present list if they are different
        if prev_list != toggledSigns_list:
            print("time: ", current_time, "list : ", toggledSigns_list)

## TEST ##
import cv2
from ultralytics import YOLO
import json

model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
cap = cv2.VideoCapture("./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")
op = ObstacleProcessor()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Empty video frame or completed processing")
        break

    frame = cv2.resize(frame, (720, 480))
    results = model.track(frame, conf=0.3, imgsz=480, verbose=False)
    obstacle_data = {
            "results": results[0].tojson() # results 변환
    }
    op.execute(obstacle_data)

cap.release()

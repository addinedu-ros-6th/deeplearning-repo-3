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
REFINED_OBJECTS = ["RedSign", "ChildZone", "SpeedLimit50", "Pedestrian", "Barricade", "WildAnimal"]
toggledSigns_dict = {objType : False for objType in REFINED_OBJECTS}
toggledSigns_list = [False] * len(REFINED_OBJECTS)
toggledSigns_prev = []
global curr_speedLimit
curr_speedLimit = 100
global prev_speedLimit
prev_speedLimit = 100

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
        self.detection_timeout = 3 #검출 해제 조건(시간)
        self.yLimit_signs = 0 #표지판 y조건
        self.yLimit_obstacle = 0 #장애물 y조건
        self.http_send_func = None
        self.socket_send_func = None


    def set_callback(self, http_send_func, socket_send_func):
        self.http_send_func = http_send_func
        self.socket_send_func = socket_send_func



    def check_detection_timeout(self, current_time): # 검출 시간이 초과되었는지 확인하고 객체의 상태를 업데이트하는 메소드
        for obj_name in list(detected_objects.keys()):
            if obj_name in ['person', 'dog', 'stop']:
                obj = detected_objects[obj_name]
                if obj.detection_status and current_time > self.detection_timeout + obj.detection_time:
                    obj.detection_count = 0
                    obj.detection_status = False

    def execute(self, data):
        global curr_speedLimit, prev_speedLimit
        current_time = time.time()
        dList = data['data']["results"]
        toggledSigns_prev = toggledSigns_list.copy()

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
                            match object_name:
                                case "Red_sign":
                                    toggledSigns_dict["RedSign"] = True
                                    if "Blue_sign" in detected_objects.keys():
                                        detected_objects["Blue_sign"].detection_status = False
                                case "Blue_sign":
                                    toggledSigns_dict["RedSign"] = False
                                    if "Red_sign" in detected_objects.keys():
                                        detected_objects["Red_sign"].detection_status = False
                    elif object_name in ['child_deactive', 'child', '50km', '50km_deactive']:
                        if obj.detection_count > self.alert_threshold and (not obj.detection_status) and obj.y_position > self.yLimit_signs:
                            obj.detection_status = True
                            obj.detection_count = 0
                            match object_name:
                                case "child" : toggledSigns_dict["ChildZone"] = True;
                                case "child_deactive": toggledSigns_dict["ChildZone"] = False
                                case "50km": toggledSigns_dict["SpeedLimit50"] = True
                                case "50km_deactive": toggledSigns_dict["SpeedLimit50"] = False
                    elif object_name in ['person', 'dog', 'stop']:
                        if obj.detection_count > self.alert_threshold and (not obj.detection_status) and obj.y_position > self.yLimit_obstacle:
                            obj.detection_status = True
                            obj.detection_count = 0
                            print("obj name : ", object_name)

        for obstacle in ["person", "stop", "dog"]:
            if obstacle not in list(detected_objects.keys()):
                continue
            obj = detected_objects[obstacle]
            match obstacle:
                case "person" : toggledSigns_dict["Pedestrian"] = obj.detection_status
                case "stop" : toggledSigns_dict["Barricade"] = obj.detection_status
                case "dog" : toggledSigns_dict["WildAnimal"] = obj.detection_status

        self.check_detection_timeout(current_time) # 검출 시간 초과 여부 확인
        # update list
        for i, obj_name in enumerate(REFINED_OBJECTS):
            toggledSigns_list[i] = toggledSigns_dict[obj_name]
        # compare present list with previous list, print present list if they are different

        if toggledSigns_prev != toggledSigns_list:
            print("time: ", current_time, "list : ", toggledSigns_list)
            self.http_send_func("icon", toggledSigns_list, "GUI")

        prev_speedLimit = curr_speedLimit

        if toggledSigns_list[1] == True: curr_speedLimit = 30
        elif toggledSigns_list[2] == True: curr_speedLimit = 50
        else: curr_speedLimit = 100
        
        if prev_speedLimit != curr_speedLimit:
            self.socket_send_func("DF", str(curr_speedLimit))





# # TEST ##
# import cv2
# from ultralytics import YOLO
# import json
#
# model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
# cap = cv2.VideoCapture("./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")
# op = ObstacleProcessor()
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Empty video frame or completed processing")
#         break
#
#     frame = cv2.resize(frame, (720, 480))
#     results = model.track(frame, conf=0.3, imgsz=480, verbose=False)
#     obstacle_data = { "data" : {"results": results[0].tojson() # results 변환
#       }
#     }
#
#     op.execute(obstacle_data)
#     cv2.imshow("Live Camera", results[0].plot())
#
#     if cv2.waitKey(1) == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

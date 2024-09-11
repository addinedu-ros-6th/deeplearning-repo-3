import cv2
import numpy as np
import sys
import time
from ultralytics import YOLO

# 객체를 관리할 클래스를 정의
class DetectedObject:
    def __init__(self, name, detection_time, width, height):
        self.name = name  # 객체 이름
        self.detection_time = detection_time  # 검출 시간
        self.width = width  # bounding box 너비
        self.height = height  # bounding box 높이
    
    def __str__(self):
        return f"Object: {self.name}, Detected at: {self.detection_time}, \
Width: {round(self.width,2)}, Height: {round(self.height,2)}"

# 객체를 관리할 딕셔너리 생성
detected_objects = {}

# 모델 및 영상 불러오기
model = YOLO("/home/kim/Downloads/model/obstacle_n.pt")

print(model.names)

cap = cv2.VideoCapture("/home/kim/Downloads/object.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Empty video frame or completed processing")
        break

    frame = cv2.resize(frame, (720, 480))
    results = model.track(frame, conf=0.3, imgsz=480)
    cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    
    # 검출된 객체 처리
    if results[0].boxes.id is not None:
        for res in results:
            for box in res.boxes:
                res_id = box.id[0].tolist()
                class_id = int(box.data[0][-1])
                object_name = model.names[class_id]  # 객체 이름
                x, y, w, h = box.xywh[0].tolist()  # bounding box 정보
                
                # 이미 해당 객체가 검출된 적이 없으면 새로 생성
                if object_name not in detected_objects:
                    detected_objects[object_name] = DetectedObject(
                        name=object_name, 
                        detection_time=time.strftime("%Y-%m-%d %H:%M:%S"), 
                        width=w, 
                        height=h
                    )
                
                # 현재 객체 정보 출력
                # print(detected_objects[object_name])
    for objname in detected_objects:
        print("\n",detected_objects[objname])

    # 결과를 보여줌
    cv2.imshow("Live Camera", results[0].plot())
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


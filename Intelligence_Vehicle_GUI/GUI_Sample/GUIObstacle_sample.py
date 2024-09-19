import cv2
import numpy as np
import sys
import time
from ultralytics import YOLO

road_img = cv2.imread("./Intelligence_Vehicle_GUI/GUI_Sample/Dataset/road.webp")
road_img = cv2.resize(road_img, (300, 100))

banana_img = cv2.imread("./Intelligence_Vehicle_GUI/GUI_Sample/Dataset/banana.jpeg")
# 임시로 모든 이미지 바나나로 처리
person_img = banana_img
dog_img = banana_img
stop_img = banana_img
img_50km = banana_img
img_50km_deactivate = banana_img
img_child = banana_img
img_child_deactivate = banana_img
RedSign_img = banana_img
BlueSign_img = banana_img
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
    
detected_objects = {}


# 모델 및 영상 불러오기
model = YOLO("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt")
cap = cv2.VideoCapture('./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        print("Empty video frame or completed processing")
        break

    frame = cv2.resize(frame, (720, 480))

    results = model.track(frame, conf=0.7, imgsz=480)
    frame = np.full_like(frame, (255, 255, 255))

    road_height, road_width = road_img.shape[:2]    
    frame_height, frame_width = frame.shape[:2]
    # 중앙 하단에 배치할 좌표 계산
    road_x = int(frame_width/2 - road_width/2)
    road_y = int(frame_height - road_height)

    road_endX = int(road_x + road_width)
    road_endY = int(road_y + road_height)
    # # 자동차 이미지를 배경에 추가
    frame[road_y: road_endY, road_x: road_endX] = road_img


    # 검출된 객체 처리
    if results[0].boxes.id is not None:
        res = results[0]
        for box in res.boxes:
            res_id = box.id[0].tolist()
            class_id = int(box.data[0][-1])
            object_name = model.names[class_id]  # 객체 이름
            x, y, w, h = box.xywh[0].tolist()  # bounding box 정보

            detected_objects[object_name] = DetectedObject(
                name=object_name, 
                detection_time=time.strftime("%Y-%m-%d %H:%M:%S"), 
                width=w, 
                height=h
            )

            if object_name == "person":
                overlay_img = person_img
            elif object_name == "dog":
                overlay_img = dog_img
            elif object_name == "stop":
                overlay_img = stop_img
            elif object_name == "50km":
                overlay_img = img_50km
            elif object_name == "50km_deactive":
                overlay_img = img_50km_deactivate
            elif object_name == "child":
                overlay_img = img_child 
            elif object_name == "child_deactive":
                overlay_img = img_child_deactivate        
            elif object_name == "Red_sign":
                overlay_img = RedSign_img
            elif object_name == "Blue_sign":
                overlay_img = BlueSign_img
            else:
                overlay_img = None

            if overlay_img is not None:
                overlay_aspect_ratio = overlay_img.shape[1] / overlay_img.shape[0]
                new_height = int(h)
                new_width = int(new_height * overlay_aspect_ratio)

                resized_overlay = cv2.resize(overlay_img, (new_width, new_height))
                
                x1 = int(x - new_width // 2)
                y1 = int(y - new_height // 2)

                # Ensure the overlay does not go out of frame boundaries
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x1 + new_width)
                y2 = min(frame.shape[0], y1 + new_height)

                resized_overlay = resized_overlay[:y2 - y1, :x2 - x1]
                frame[y1:y2, x1:x2] = resized_overlay

    # cv2.imshow("Live Camera", results[0].plot())
    
    cv2.imshow("Live Camera", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
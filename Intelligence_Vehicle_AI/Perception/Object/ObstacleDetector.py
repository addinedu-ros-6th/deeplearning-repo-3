import base64
import cv2
import numpy as np
import sys
import time

from sympy import false
from ultralytics import YOLO

class ObstacleDetector:

    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path, verbose=False)
        self.cap = cv2.VideoCapture(video_path)


    def start_detect_result(self, image, send_func):
        copy_image = image.copy()
        _, buffer = cv2.imencode('.jpg', copy_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        image_data = {
            "type": "obstacle",
            "image": encoded_image
        }
        
        send_func("viewer", image_data , "GUI")

        try:
            results = self.model.track(image, conf=0.7, verbose=False)
            obstacle_data = {
                "results": results[0].tojson() # results 변환
            }
        except Exception as e:
            print(f"Error processing image: {e}")
            obstacle_data = {"data": str(e)}
        send_func("obstacle", obstacle_data, "Service")


    def get_results(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Empty video frame or completed processing")
                break

            frame = cv2.resize(frame, (720, 480))
            results = self.model.track(frame, conf=0.7, imgsz=480, verbose=False)

            yield results, frame

            if cv2.waitKey(1) == ord('q'):
                break

            

        self.cap.release()

# test = ObstacleDetector("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt",
#                         "./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")
# x = test.get_results()
# print("x: ", x)


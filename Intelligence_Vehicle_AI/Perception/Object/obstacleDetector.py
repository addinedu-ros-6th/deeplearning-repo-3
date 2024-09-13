import cv2
import numpy as np
import sys
import time
from ultralytics import YOLO

class ObstacleDetector:

    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_path)

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Empty video frame or completed processing")
                    break

                frame = cv2.resize(frame, (720, 480))
                results = self.model.track(frame, conf=0.7, imgsz=480, verbose=False)
                json_result = results[0].tojson()
                print(json_result)

                if cv2.waitKey(1) == ord('q'):
                    break
        finally:
            self.cap.release()

# test = ObstacleDetector("./Intelligence_Vehicle_AI/Perception/Object/obstacle_n.pt",
#                         "./Intelligence_Vehicle_AI/Dataset/Object_dataset/object.mp4")
# test.run()

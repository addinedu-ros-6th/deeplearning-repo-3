import cv2
import numpy as np
from ultralytics import YOLO

class LaneDetector:
    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_path)
        self.newlist = []
        self.error = 0
        self.stop_line_flag = 0

    def find_lane_centers(self, lane_mask, image_width):
        left_lane_points = []
        right_lane_points = []

        for mask in lane_mask:
            x_coords = mask[:, 0]
            y_coords = mask[:, 1]
            
            if np.mean(x_coords) < image_width / 2:
                left_lane_points.extend(zip(x_coords, y_coords))
            else:
                right_lane_points.extend(zip(x_coords, y_coords))

        left_lane_center = np.mean(left_lane_points, axis=0) if left_lane_points else None
        right_lane_center = np.mean(right_lane_points, axis=0) if right_lane_points else None

        return left_lane_center, right_lane_center

    def process_video(self):
        while self.cap.isOpened():
            ret, image = self.cap.read()
            if not ret:
                break

            results = self.model(image)
            self.stop_line_flag = 1 if 'Stop_Line' in self.newlist else 0

            lane_masks = results[0].masks.xy
            class_ids = results[0].boxes.cls

            filtered_masks = [mask for mask, class_id in zip(lane_masks, class_ids) if class_id in [1, 2]]
            lane_mask = filtered_masks

            current_objects = [self.model.names[int(box.cls[0])] for result in results for box in result.boxes]
            self.update_object_list(current_objects)

            image_width = image.shape[1]
            image_height = image.shape[0]

            left_center, right_center = self.find_lane_centers(lane_mask, image_width)

            if left_center is not None:
                cv2.circle(image, (int(left_center[0]), int(left_center[1])), 5, (0, 255, 0), -1)
                cv2.putText(image, f"Left: ({int(left_center[0])}, {int(left_center[1])})", 
                            (int(left_center[0]) + 10, int(left_center[1]) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            if right_center is not None:
                cv2.circle(image, (int(right_center[0]), int(right_center[1])), 5, (0, 0, 255), -1)
                cv2.putText(image, f"Right: ({int(right_center[0])}, {int(right_center[1])})", 
                            (int(right_center[0]) + 10, int(right_center[1]) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            if left_center is not None and right_center is not None:
                middle_point = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)
                cv2.circle(image, (int(middle_point[0]), int(middle_point[1])), 5, (255, 0, 0), -1)
                cv2.putText(image, f"Middle: ({int(middle_point[0])}, {int(middle_point[1])})", 
                            (int(middle_point[0]) + 10, int(middle_point[1]) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

                center_x = image_width // 2
                self.error = round((center_x - middle_point[0]), 1)

                # 중앙 선 그리기
                cv2.line(image, (center_x, 0), (center_x, image_height), (255, 0, 255), 2)

                # error 시각화
                color = (0, 255, 0) if abs(self.error) < 10 else (0, 255, 255) if abs(self.error) < 20 else (0, 0, 255)
                cv2.line(image, (int(middle_point[0]), int(middle_point[1])), (center_x, int(middle_point[1])), color, 2)

            # 텍스트 표시
            cv2.putText(image, f"Error: {self.error}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, f"Stop Line Flag: {self.stop_line_flag}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imshow('Lane Centers', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def update_object_list(self, current_objects):
        for obj in current_objects:
            if obj not in self.newlist:
                self.newlist.append(obj)

        for obj in self.newlist[:]:
            if obj not in current_objects:
                self.newlist.remove(obj)

    def get_error(self):
        print('errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
        return self.error

    def get_stop_line_flag(self):
        return self.stop_line_flag

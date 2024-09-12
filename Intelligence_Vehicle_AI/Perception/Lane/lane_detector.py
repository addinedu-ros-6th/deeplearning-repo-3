import cv2
import numpy as np
from ultralytics import YOLO

class LaneDetection:
    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path)  # YOLOv8 모델 로드
        self.cap = cv2.VideoCapture(video_path)  # 비디오 파일 열기
        self.newlist = []  # 실시간 객체 검출을 위한 리스트
        cv2.namedWindow('Lane Centers')  # 윈도우 이름

    def find_lane_centers(self, lane_mask):
        left_lane_points = []  # 좌측 차선 포인트 저장 리스트
        right_lane_points = []  # 우측 차선 포인트 저장 리스트

        for mask in lane_mask:
            x_coords = mask[:, 0]  # x 좌표
            y_coords = mask[:, 1]  # y 좌표
            
            if np.mean(x_coords) < image.shape[1] / 2:
                left_lane_points.extend(zip(x_coords, y_coords))  # 좌측 차선 포인트 추가
            else:
                right_lane_points.extend(zip(x_coords, y_coords))  # 우측 차선 포인트 추가

        left_lane_center = np.mean(left_lane_points, axis=0) if left_lane_points else None
        right_lane_center = np.mean(right_lane_points, axis=0) if right_lane_points else None

        return left_lane_center, right_lane_center  # 좌측 및 우측 차선 중앙 반환

    def update_objects(self, current_objects):
        # newlist에 없는 새로운 객체 추가
        for obj in current_objects:
            if obj not in self.newlist:
                self.newlist.append(obj)

        # 더 이상 탐지되지 않은 객체를 newlist에서 제거
        for obj in self.newlist[:]:  # 리스트 복사본을 사용하여 안전하게 제거
            if obj not in current_objects:
                self.newlist.remove(obj)

    def process_video(self):
        while self.cap.isOpened():
            ret, image = self.cap.read()  # 프레임 읽기
            if not ret:
                break

            results = self.model(image)  # 모델을 사용하여 결과 얻기
            lane_masks = results[0].masks.xy  # 마스크 데이터
            class_ids = results[0].boxes.cls  # 클래스 ID

            # 클래스 ID가 1 또는 2인 마스크만 추출
            filtered_masks = []
            for mask, class_id in zip(lane_masks, class_ids):
                if class_id in [1, 2]:  # 클래스 ID가 1 또는 2일 경우
                    filtered_masks.append(mask)

            lane_mask = filtered_masks
            current_objects = [model.names[int(box.cls[0])] for result in results for box in result.boxes]  # 탐지된 객체 리스트

            self.update_objects(current_objects)  # 객체 업데이트

            left_center, right_center = self.find_lane_centers(lane_mask)  # 차선 중앙 계산

            if left_center is not None:
                cv2.circle(image, (int(left_center[0]), int(left_center[1])), 5, (0, 255, 0), -1)  # 좌측 중앙 표시

            if right_center is not None:
                cv2.circle(image, (int(right_center[0]), int(right_center[1])), 5, (0, 0, 255), -1)  # 우측 중앙 표시

            # mid_point 계산
            if left_center is not None and right_center is not None:
                middle_point = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)  # 중간 점 계산
                cv2.circle(image, (int(middle_point[0]), int(middle_point[1])), 5, (255, 0, 0), -1)  # 중간 점 표시
                mid_point_text = f"mid_point: ({int(middle_point[0])}, {int(middle_point[1])})"  # 중간 점 텍스트
                cv2.putText(image, mid_point_text, (int(middle_point[0]) + 10, int(middle_point[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                center_x = image.shape[1] // 2
                error = round((center_x - middle_point[0]), 1)  # 에러 계산
                error_text = f"error: {error:.1f}"  # 에러 텍스트
                cv2.putText(image, error_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                print("error값 :{}".format(error))
                cv2.line(image, (center_x, 0), (center_x, image.shape[0]), (255, 0, 255), 2)  # 중앙 세로선

                # error 시각화
                color = (0, 255, 0) if abs(error) < 10 else (0, 255, 255) if abs(error) < 20 else (0, 0, 255)
                cv2.line(image, (int(middle_point[0]), int(middle_point[1])), (center_x, int(middle_point[1])), color, 2)

            stop_line_text = f"Stop Line Flag: {1 if 'Stop_Line' in self.newlist else 0}"  # Stop_Line 플래그 텍스트
            cv2.putText(image, stop_line_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            print("현재 탐지된 객체:", self.newlist)
            cv2.imshow('Lane Centers', image)  # 이미지 표시

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()  # 웹캠 해제
        cv2.destroyAllWindows()  # 모든 윈도우 닫기

# 사용 예
if __name__ == "__main__":
    lane_detector = LaneDetection('/home/heechun/dev_ws/deeplearning-repo-3/Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                                  '/home/heechun/dev_ws/deeplearning-repo-3/Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')
    lane_detector.process_video()

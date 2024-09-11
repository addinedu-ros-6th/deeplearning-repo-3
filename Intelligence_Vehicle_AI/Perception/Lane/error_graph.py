#%%
# 필요한 라이브러리 임포트
import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt

# YOLOv8 모델 로드
model = YOLO('/home/heechun/dev_ws/#3 dl_project_folder/03_lane/runs/segment/train/weights/best_v8n_seg.pt')

# 비디오 파일 열기
# cap = cv2.VideoCapture('/home/heechun/dev_ws/#3 dl_project_folder/02_rasberry/0906_test/Dataset/video/lane_data/lane_sum_video.mp4')
cap = cv2.VideoCapture('/home/heechun/dev_ws/#3 dl_project_folder/02_rasberry/0906_test/Dataset/video/lane_data/30_only_lane_video_fast.mp4')
cv2.namedWindow('Lane Centers')

# 실시간 객체 검출을 위한 리스트
newlist = []
error_log = []  # 에러 값을 저장할 리스트

# 좌우 차선의 중앙 계산 함수
def find_lane_centers(lane_mask):
    left_lane_points = []
    right_lane_points = []
    for mask in lane_mask:
        x_coords = mask[:, 0]
        y_coords = mask[:, 1]
        
        if np.mean(x_coords) < image.shape[1] / 2:
            left_lane_points.extend(zip(x_coords, y_coords))
        else:
            right_lane_points.extend(zip(x_coords, y_coords))

    left_lane_center = np.mean(left_lane_points, axis=0) if left_lane_points else None
    right_lane_center = np.mean(right_lane_points, axis=0) if right_lane_points else None

    return left_lane_center, right_lane_center

# 실시간 웹캠 프레임 처리
while cap.isOpened():
    ret, image = cap.read()
    if not ret:
        break

    results = model(image)
    stop_line_flag = 1 if 'Stop_Line' in newlist else 0

    lane_masks = results[0].masks.xy
    class_ids = results[0].boxes.cls

    filtered_masks = []
    for mask, class_id in zip(lane_masks, class_ids):
        if class_id in [1, 2]:
            filtered_masks.append(mask)

    lane_mask = filtered_masks

    current_objects = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            current_objects.append(class_name)

    for obj in current_objects:
        if obj not in newlist:
            newlist.append(obj)

    for obj in newlist[:]:
        if obj not in current_objects:
            newlist.remove(obj)

    left_center, right_center = find_lane_centers(lane_mask)

    if left_center is not None:
        cv2.circle(image, (int(left_center[0]), int(left_center[1])), 5, (0, 255, 0), -1)

    if right_center is not None:
        cv2.circle(image, (int(right_center[0]), int(right_center[1])), 5, (0, 0, 255), -1)

    if left_center is not None and right_center is not None:
        middle_point = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)
        cv2.circle(image, (int(middle_point[0]), int(middle_point[1])), 5, (255, 0, 0), -1)

        center_x = image.shape[1] // 2
        error = center_x - middle_point[0]
        error_log.append(error)  # error 값을 기록
        error_text = f"error: {error:.2f}"
        cv2.putText(image, error_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        print("error값 :{}".format(error))

        cv2.line(image, (center_x, 0), (center_x, image.shape[0]), (255, 0, 255), 2)

        if abs(error) < 10:
            color = (0, 255, 0)
        elif abs(error) < 20:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.line(image, (int(middle_point[0]), int(middle_point[1])), (center_x, int(middle_point[1])), color, 2)

    stop_line_text = f"Stop Line Flag: {stop_line_flag}"
    cv2.putText(image, stop_line_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    print("현재 탐지된 객체:", newlist)

    cv2.imshow('Lane Centers', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# 그래프 그리기
plt.figure(figsize=(10, 5))
plt.plot(error_log, label='Error', color='blue')
plt.title('Error over Frames')
plt.xlabel('Frame')
plt.ylabel('Error Value')
plt.axhline(0, color='red', linestyle='--')  # 0 에러 기준선
plt.legend()
plt.grid()
plt.show()

# %%

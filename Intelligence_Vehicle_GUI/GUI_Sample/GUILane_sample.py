import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt 

model = YOLO("./Intelligence_Vehicle_AI/Perception/Lane/best_v8s_seg.pt")
car_img = cv2.imread("./Intelligence_Vehicle_GUI/GUI_Sample/Dataset/car.png")
car_img = cv2.resize(car_img, (300, 150))
cap = cv2.VideoCapture('./Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        break
    masked_image = np.full_like(img, (255, 255, 255))

    results = model(img)
    r = results[0]

    masks = r.masks  # 세그멘테이션 마스크
    classes = r.names  # 클래스 이름
    boxes = r.boxes.xyxy
        
    for (mask, cls, box_xyxy) in zip(masks.data, r.boxes.cls, boxes):
        mask_np = mask.cpu().numpy()  # Tensor를 NumPy 배열로 변환
        mask_resized = cv2.resize(mask_np, (img.shape[1], img.shape[0]), 
        interpolation=cv2.INTER_NEAREST)    
        # 클래스에 따른 색 설정 (정지선, 왼쪽 차선, 오른쪽 차선)
        if cls == 0:  # 정지선
            color = (125, 125, 125)  # 빨간색
        elif cls == 1:  # 왼쪽 차선
            color = (50, 50, 50)  
        elif cls == 2:  # 오른쪽 차선
            color = (50, 50, 50) 
        else:
            continue  # 관심 없는 클래스는 무시
        # 마스크를 이미지에 적용
        mask_resized = mask_resized.astype(bool)  # 마스크를 이진화
        masked_image[mask_resized] = color  # 마스크 위치에 색칠
        masked_image = cv2.blur(masked_image, ksize = (5, 5))

        x1, y1, x2, y2 = map(int, box_xyxy)
        # print(box_xyxy)

    car_height, car_width = car_img.shape[:2]    
    img_height, img_width = masked_image.shape[:2]
    # 중앙 하단에 배치할 좌표 계산
    car_x = int(img_width/2 - car_width/2)
    car_y = int(img_height - car_height)

    car_endX = int(car_x + car_width)
    car_endY = int(car_y + car_height)
    # 자동차 이미지를 배경에 추가
    masked_image[car_y: car_endY, car_x: car_endX] = car_img

    cv2.imshow("masked_image", masked_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# cv2.waitKey()
cap.release() 
cv2.destroyAllWindows()
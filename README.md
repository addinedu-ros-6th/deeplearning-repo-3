# IV Project
차선인식 기반 자율주행 시스템 프로젝트

## 1. 개요
(데모 영상)

https://drive.google.com/file/d/1wHXQA6brI9wGeNsBYWnBAAHrJa71_X6w/view?usp=sharing
https://drive.google.com/file/d/1Vh_ztGSVTv9K7oVbI3sXrSjJfdcepeMJ/view?usp=sharing


### 1.1. 프로젝트 설명
### 1.2. 기술 스택
|분류|기술|
|-----|-----|
|개발 환경|Linux|
|개발 언어|Python, C++|
|하드웨어|RaspberryPi, Arduino|
|딥러닝 프레임워크|Ultralytics YOLOv8|
|통신 프로토콜|UDP, HTTP|
|DBMS|MySQL|
|UI|PyQT|
|영상 처리|openCV|
### 1.3. 팀 구성
|성명|담당|
|----|-----|
|윤희천 <br> (Project Leader)|차선 인식 모델 학습 <br> 차선 인식 로직 개발, 제어 로직 지원| 
|김재창|객체 탐지 모델 학습 <br> 객체 탐지 로직 개발, GUI 개발|
|서영환|DB 환경 구축, GUI 개발 <br> 객체 탐지 모델 학습| 
|이경민|제어 로직 개발, 객체 탐지 모델 학습 <br> 차선 인식 로직 지원|
|조전욱|통신 환경 구축, 객체 탐지 모델 학습 <br> 시스템 설계, 구현 및 시스템 통합|
### 1.4. 협업 툴
- Confluence: 프로젝트 문서 및 지식 공유
- Jira: 프로젝트 관리 및 이슈 트래킹
- Git: 형상 관리 및 프로젝트 공유

## 2. 시스템 개발
딥러닝 기술의 적용, 센서에서 수집한 대량 데이터의 처리, 여러 산업에 적용될 수 있는 확장성, 다양한 연구 분야와의 연계성을 고려하여 카메라 영상을 기반으로 한 자율주행 로봇을 프로젝트 주제로 선정
### 2.1. 주요 기능 
(주요 기능 테이블)

- 주행 관련 객체 인식 기능
장애물(보행자, 야생동물, 바리케이드 등), 차선, 신호, 표지판 인식 후 메인 프로그램으로 인식 정보 송신
- 주행 모니터링 기능
객체 검출용 카메라 및 차선 검출용 카메라 영상 출력, 표지판 내용, 장애물 정보 등 알람, 현재 속도 표시
- 주행 기록 관리 기능
주행 기록(검출 내역, 시간, 속도 등) 저장 및 조회 
- 주행 상태 제어 기능
차선 유지를 위한 횡방향 제어, 도로 환경 조건에 따라 변화하는 종방향 제어
  
### 2.2. 시스템 아키텍처
#### 하드웨어 구조
![hardware](https://github.com/user-attachments/assets/e793c40f-491b-4d63-8d04-106b6e3c24c1)
#### 소프트웨어 구조
#### 시나리오 설계
- 차선 검출 시나리오
    
![sequence_lane1](https://github.com/user-attachments/assets/7db9002c-4d24-4c77-beda-08a4e25903b1)

- 장애물 검출 시나리오
    
![sequence_lane (1)](https://github.com/user-attachments/assets/ad45240c-29f7-4031-8746-643ae64fcabb)

#### 클래스 구성

![Screenshot from 2024-10-17 14-44-10](https://github.com/user-attachments/assets/5bde5749-b5b4-4788-8342-8cb3b4aac7a9)

- 코드 설명(Best Practice 적용): 코드 효율성, 확장성, 가독성을 고려한 설계 등
(생성 패턴: 팩토리 메서드, 빌더, 싱글턴 / 행동 패턴: 전략)

#### 데이터베이스 구조

![erd](https://github.com/user-attachments/assets/9d43f6bd-cfd1-4fda-aece-ae4cf4ae6320)

#### UI 화면 구성

![0925121521730420](https://github.com/user-attachments/assets/b6db7a78-0eb2-47d3-aa2a-0b1902b0229b)

#### 주행 제어
- 시스템 동작 알고리즘

- 주행 알고리즘

![abstract_driving_algo](https://github.com/user-attachments/assets/3943f5f7-bf7a-435f-88d0-35360cad3c63)

### 2.2. 딥러닝 모델 생성
#### 차선 검출 모델
- 모델 : YOLOv8 segmentation (nano)
- 목적 : 차량 제어에 필요한 정보를 제공하기 위해 정지선과 차선(왼쪽 차선, 오른쪽 차선)을 구분해 검출
- 데이터 준비 : 테스트 트랙을 직접 돌면서 녹화한 영상에서 학습용으로 1,000장의 이미지를 추출하여 사용
- 라벨링 도구 : Labelme 툴을 활용해 정지선, 왼쪽 차선, 오른쪽 차선을 각각 폴리곤(polygon) 방식으로 라벨링
- 카메라 : C920 카메라
  
|학습 데이터 분량|데이터 취득 방식|클래스 리스트|
|-----|-----|-----|
|1000장|모형 도로 촬영|[Stop_Line, L_Lane, R_Lane]|
- 차선 모델 loss, mAP 그래프

![lane_merge1](https://github.com/user-attachments/assets/a5d272b0-edc9-4640-af1c-f3be448986cc)

- Loss 감소(train/val box, cls, dfl loss):
  - train과 val 손실이 지속적으로 감소하며, 학습이 잘 진행된거를 보여줌
  - 검증 손실(val)이 학습 손실(train)과 유사하게 수렴하므로 과적합이 없고 안정적인 학습이 이루어졌다고 보여짐
- Precision/Recall 및 mAP (B):
  - Precision과 Recall(B)의 값이 50 에포크 이후보터 0.96~0.98 이상으로 안정화 되었음
  - mAP50 및 mAP50-95 지표 또한 시간이 지남에 따라 향상되어, 0.9에 가까운 성능을 달성했음

해석: 학습과 검증 데이터에서 모두 좋은 성능을 보여주어, 작업에 안정적으로 적용될 수 있는것으로 보여짐

- class 데이터 및 val이미지 

![lane_merge2](https://github.com/user-attachments/assets/010ff9f2-935a-48c6-81d1-09731d13d89e)

- 왼쪽 상단 그래프: 차선 종류별 인식 빈도 그래프
- 오른쪽 상단 그래프: 차선 바운딩 박스들이 일관되게 정렬된 것을 볼 수 있음
- 하단 히트맵: 차선의 위치 및 크기 분포를 볼 수 있는 그래프
  - 차선의 X, Y 좌표와 너비, 높이가 일정한 패턴을 가지며 인식되었음을 보여줌
- 오른쪽 사진들: 장애물 인식 시각화(validation 사진)
  - 각각의 사진에서 객체가 정확하게 탐지되고 표시된걸 확인할 수 있음
 
해석: 로봇이 도로 환경에서 차선과 정지선을 일관되게 인식할 수 있음을 보여줌


#### 객체 검출 모델
- 모델 : YOLOv8 object detection (nano)
- 목적 : 차량 제어에 필요한 장애물(신호등, 표지판 사람 등)을 검출
- 데이터 준비 : 테스트 트랙을 집적 돌면서 녹화한 영상에서 학습용으로 1,200장의 이미지를 추출하여 사용
- 라벨링 도구 : Labelme 툴을 활용해 신호등, 표지판, 사람 등을 폴리곤(polygon) 방식으로 라벨링
- 카메라 : SY101-A 카메라
  
|학습 데이터 분량|데이터 취득 방식|클래스 리스트|
|-----|-----|-----|
|1200장|모형 도로 촬영|[Red_Sign, Blue_Sign, Child, Child_deactivate, 50km, 50km_deactivate, person, child, dog]|
- 객체 모델 loss, mAP 그래프
  
![obstacle_result](https://github.com/user-attachments/assets/046bb048-d95b-48f2-a2ef-8e6a30044abd)

- Loss 감소(train/val bbox, cls, dfl loss):
  - train과 val 손실이 지속적으로 감소하며, 학습이 잘 진행된거를 보여줌
  - 검증 손실(val)이 학습 손실(train)과 유사하게 수렴하므로 과적합이 없고 안정적인 학습이 이루어졌다고 보여짐
- Precision/Recall 및 mAP (B):
  - Precision과 Recall(B)의 값이 50 에포크 이후부터 0.96~0.98 이상으로 안정화 되었음
  - mAP50 및 mAP50-95 지표 또한 시간이 지남에 따라 향상되어, 0.9에 가까운 성능을 달성했음
  
해석: 학습과 검증 데이터에서 모두 좋은 성능을 보여주며, 작업에 안정적으로 적용될 수 있는것으로 보여짐

- class 데이터 및 val이미지 

![object_merge](https://github.com/user-attachments/assets/c35aee99-63d5-4ffe-b6a4-bc71ca4a6f27)

- 왼쪽 상단 그래프: 클래스별 개수를 한 눈에 볼수 있는 그래프
- 오른쪽 상단 그래프: 다양한 객체들의 바운딩 박스 크기와 위치 분포를 겹쳐서 보여줌
- 하단 히트맵: 객체의 위치 및 크기 분포를 볼 수 있는 그래프
  - X,Y 좌표와 Width, Height에 따른 객체 인식 분포를 보여주며, 객체들이 다양한 위치와 크기로 인식되었음을 보여줌
- 오른쪽 사진들: 장애물 인식 시각화(validation 사진)
  - 각각의 사진에서 객체가 정확하게 탐지되고 표시된걸 확인할 수 있음

해석: 로봇이 도로 환경에서 다양한 장애물과 신호를 정확하게 인식할 수 있음을 보여줌
  
  
### 2.3. 구현
- 구현
  Commit 로그, 생성한 파일 등

- 시연 영상
Click here to watch the demo

## 3. 결론
### 3.1. 문제 해결 과정
- 영상 송출 관련
- 하드웨어 성능 관련
- 제어 관련
### 3.2. 향후 개선 방안 및 확장 가능성

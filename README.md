# deeplearning-repo-3
딥러닝 프로젝트 3조. 인지 능력을 갖춘 차선 인식 기반의 자율주행 차량 

## 개요
### 프로젝트 목표
### 팀 구성
|성명|담당|
|----|-----|
|윤희천 <br> (Project Leader)|차선 인식 모델 학습 <br> 차선 인식 로직 개발, 제어 로직 지원| 
|김재창|객체 탐지 모델 학습 <br> 객체 탐지 로직 개발, GUI 개발|
|서영환|DB 환경 구축, GUI 개발 <br> 객체 탐지 모델 학습| 
|이경민|제어 로직 개발, 객체 탐지 모델 학습 <br> 차선 인식 로직 지원|
|조전욱|통신 환경 구축, 객체 탐지 모델 학습 <br> 시스템 설계, 구현 및 시스템 통합|
### 협업
- Confluence: 프로젝트 문서 및 지식 공유
- Jira: 프로젝트 관리 및 이슈 트래킹
- Git: 형상 관리 및 프로젝트 공유
### 기술 스택
|분류|기술|
|-----|-----|
|개발 환경|Linux|
|개발 언어|Python, C++|
|하드웨어|RaspberryPi|
|딥러닝 프레임워크|Ultralytics YOLOv8|
|통신 프로토콜|UDP, HTTP|
|DBMS|MySQL|
|UI|PyQT|
|영상 처리|openCV|
## 프로젝트 단계
### 주제 선정
딥러닝 기술의 적용, 센서에서 수집한 대량 데이터의 처리, 여러 산업에 적용될 수 있는 확장성, 다양한 연구 분야와의 연계성을 고려하여 카메라 영상을 기반으로 한 자율주행 로봇을 프로젝트 주제로 선정
### 사용자 요구사항 분석
- 주행 관련 객체 인식 기능
  장애물(보행자, 야생동물, 바리케이드 등), 차선, 신호, 표지판 인식 후 메인 프로그램으로 인식 정보 송신
- 주행 모니터링 기능
  객체 검출용 카메라 및 차선 검출용 카메라 영상 출력, 표지판 내용, 장애물 정보 등 알람, 현재 속도 표시
- 주행 기록 관리 기능
  주행 기록(검출 내역, 시간, 속도 등) 저장 및 조회 
- 주행 상태 제어 기능
  차선 유지를 위한 횡방향 제어, 도로 환경 조건에 따라 변화하는 종방향 제어
  

### 시스템 설계
- 시스템 구조도
![system_architecture](https://github.com/user-attachments/assets/be74edc8-9306-4ccd-9494-87cf21cf4ec3)
- 주요 시나리오
  - 차선 검출 시나리오
![sequence_lane1](https://github.com/user-attachments/assets/7db9002c-4d24-4c77-beda-08a4e25903b1)
  - 장애물 검출 시나리오
![sequence_lane (1)](https://github.com/user-attachments/assets/ad45240c-29f7-4031-8746-643ae64fcabb)

#### 소프트웨어 설계
클래스 다이어그램
- 코드 설명(Best Practice 적용)
  코드 효율성, 확장성, 가독성을 고려한 설계 등
- 생성 패턴: 팩토리 메서드, 빌더, 싱글턴
- 행동 패턴: 전략

server-client 구조
- Flask HTTP 메서드

ERD

![erd](https://github.com/user-attachments/assets/9d43f6bd-cfd1-4fda-aece-ae4cf4ae6320)

UI 구조
![gui_structure](https://github.com/user-attachments/assets/e14f82ce-8122-4441-bf51-14b57c5dcbd9)

제어
- 제어 알고리즘
### 딥러닝 모델 생성
#### 차선 검출 모델
|학습 데이터 분량|데이터 취득 방식|클래스 리스트|
|-----|-----|-----|
|1000장|모형 도로 촬영|[Stop_Line, L_Lane, R_Lane]|
#### 차선 모델 loss, mAP 그래프
![obstacle_result](https://github.com/user-attachments/assets/046bb048-d95b-48f2-a2ef-8e6a30044abd)
#### class 데이터 및 val이미지 예시
![object_merge](https://github.com/user-attachments/assets/c35aee99-63d5-4ffe-b6a4-bc71ca4a6f27)

#### 객체 검출 모델
|학습 데이터 분량|데이터 취득 방식|클래스 리스트|
|-----|-----|-----|
|1200장|모형 도로 촬영|[Red_sign, Blue_sign, person, child, dog, 50km, 50km_deactive, child, child_deactive]|
#### 객체 모델 loss, mAP 그래프
![lane_merge1](https://github.com/user-attachments/assets/a5d272b0-edc9-4640-af1c-f3be448986cc)
#### class 데이터 및 val이미지 예시
![lane_merge2](https://github.com/user-attachments/assets/010ff9f2-935a-48c6-81d1-09731d13d89e)

### 구현 및 시현 영상
- 구현
  Commit 로그, 생성한 파일 등
![0925121521730420](https://github.com/user-attachments/assets/b6db7a78-0eb2-47d3-aa2a-0b1902b0229b)

- 시연 영상
Click here to watch the demo

## 결론
### 문제 해결 과정
- 영상 송출 관련
- 하드웨어 성능 관련
- 제어 관련
### 향후 개선 방안 및 확장 가능성

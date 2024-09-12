from __future__ import annotations
from abc import ABC, abstractmethod
import cv2

class ObstacleSubject:
    def __init__(self, key, observer: DetectObserver):
        self._detectEvents = {}
        self._detectEvents[key] = observer
        self._observers: list[DetectObserver] = []

    def attach(self, observer: DetectObserver):
        self._observers.append(observer)

    def detach(self, observer: DetectObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, obstacle_type: str):
        for observer in self._observers:
            observer.update(obstacle_type)
        
        self._observers.clear()


class DetectObserver(ABC):
    def __init__(self, blink_massage_func):
        self.blink_massage_func = blink_massage_func

    @abstractmethod
    def update(self):
        pass

class DetectDog(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)
    
    def update(self):
        text = "떠돌이 개가 앞을 가로막습니다. 정지하세요"
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.")


class DetectDogCancel(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        # 모터를 제어하는 클래스의 멤버함수에 maxSpeed를 0으로 호출한다.
        text = "개가 도망갔습니다. 다시 주행을 시작하세요."
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.")


class DetectTrafficLightRed(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "빨간 불입니다. 정지선에 맞춰 멈추세요." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.")  


class DetectTrafficLightBlue(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "초록 불입니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 


class DetectPerson(DetectObserver):
    def __init__(self, blink_massage_func) -> None:
        super().__init__(blink_massage_func)
    
    def update(self):
        text = "술 취한 행인이 도로에서 나대고 있습니다. 주행을 멈추세요." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 


class DetectPersonCancel(DetectObserver):
    def __init__(self, blink_massage_func) -> None:
        super().__init__(blink_massage_func)
    
    def update(self):
        text = "술 취한 행인이 도망갔습니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 


class DetectSpeedLimitSign(DetectObserver):
    def __init__(self, blink_massage_func) -> None:
        super().__init__(blink_massage_func)

    def update(self):
        text = "속도 제한 구역입니다. 최대 속도를 50km로 줄이세요." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.")         


class DetectSpeedCancellation(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "속도 제한 구역을 벗어났습니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 


class DetectChildZone(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "어린이 보호 구역입니다. 조심하세요." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 


class DetectChildCancellation(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "어린이 보호 구역을 벗어났습니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 

class DetectStop(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "바리바겟트를 만났습니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 

class DetectStopCancel(DetectObserver):
    def __init__(self, blink_massage_func):
        super().__init__(blink_massage_func)

    def update(self):
        text = "바리바겟트를 누가 치웠습니다." 
        self.blink_massage_func(text)
        print("DB에 데이터를 저장합니다.") 
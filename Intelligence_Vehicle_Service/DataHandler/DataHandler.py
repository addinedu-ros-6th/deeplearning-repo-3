from abc import ABC, abstractmethod
import threading

import cv2

class DataHandler(ABC):
    @abstractmethod
    def handle(self, data, client_address):
        pass

class ObstacleImageHandler(DataHandler):
    def handle(self, data, client_address):
        print(f"ObstacleImageHandler Handling data from {client_address}: {data}")

class LaneImageHandler(DataHandler):
    def handle(self, data, client_address):
        print(f"LaneImageHandler Handling data from {client_address}: {data}")
        target = lambda: cv2.imshow(str(client_address),data[1])
        threading.Thread(target=target).start()
        

class SpeedDataHandler(DataHandler):
    def handle(self, data, client_address):
        print(f"Handling data from {client_address}: {data}")
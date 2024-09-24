from abc import ABC, abstractmethod
import base64
import threading

import cv2

class DataHandler(ABC):
    @abstractmethod
    def register_data_received_callback(self, func_tuple):
        pass
    
    @abstractmethod
    def handle(self, data, client_address):
        pass

class ObstacleImageHandler(DataHandler):
    def register_data_received_callback(self, func_tuple):
        self.dect_func = func_tuple[0]
        self.send_func = func_tuple[1]


    def handle(self, data, client_address):
        # print("\033[96mObstacleImageHandler\033[0m")
        image = data[1]
        threading.Thread(target=self.dect_func, args=(image, self.send_func, )).start()



class LaneImageHandler(DataHandler):
    def register_data_received_callback(self, func_tuple):
        self.dect_func = func_tuple[0]
        self.send_func = func_tuple[1]


    def handle(self, data, client_address):
        # print(f"LaneImageHandler Handling data from {client_address}: {data}")
        image = data[1]
        threading.Thread(target=self.dect_func, args=(image, self.send_func, )).start()


class SpeedDataHandler(DataHandler):
    def __init__(self):
        self.send_func = None
    def register_data_received_callback(self, func_tuple):
        self.send_func = func_tuple[0]

    def handle(self, data, client_address):
        print(f"Handling data from {client_address}: {data}")
        self.send_func("speed", data , "GUI")



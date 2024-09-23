import sys
import os
from typing import Callable
current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트의 디렉토리를 가져오고, 프로젝트 루트로 이동하는 상대 경로를 추가
relative_path = os.path.join(current_dir, '../../')  # 상위 폴더로 이동
sys.path.append(relative_path)

from Intelligence_Vehicle_Communicator.TCPClientNewVersion import TCPClient, TCPClientManager
from Intelligence_Vehicle_Service.Processor.Processor import Processor
import numpy as np
import json

WIDTH = 320


class LaneProcessor(Processor):
    def __init__(self):
        self.newlist = []
        self.stop_line_flag = 0
        self.error = 0
        self.error_callback = None

    def set_error_callback(self, callback):
        self.error_callback = callback
        
    def execute(self, data):
        results_json = data['data']['results']
        results = json.loads(results_json)

        # print("\033[94mLaneProcessor\033[0m")

        lane_masks = []
        class_ids = []

        for result in results:
            self.update_object_list([result['name']])

            if result['name'] in ['L_Lane', 'R_Lane']:
                lane_masks.append(np.array(list(zip(result['segments']['x'], result['segments']['y']))))
                class_ids.append(result['class'])

        self.stop_line_flag = 1 if 'Stop_Line' in self.newlist else 0

        # print(f"차선 마스크: {lane_masks}")
        # print(f"클래스 ID: {class_ids}")

        # 차선 데이터 처리
        self.process_lane_data(lane_masks, results)
      

    def process_lane_data(self, lane_masks, results):
        if not results:
            return;
        # if lane_masks:
        #     print(f"감지된 차선 수: {len(lane_masks)}")

        left_center, right_center = self.find_lane_centers(lane_masks)
        print(f' ==> Line 52: \033[38;2;118;75;166m[right_center]\033[0m({type(right_center).__name__}) = \033[38;2;39;214;70m{right_center}\033[0m')
        print(f' ==> Line 52: \033[93m[left_center]\033[0m({type(left_center).__name__}) = \033[38;2;21;58;104m{left_center}\033[0m')
        
        if left_center is not None and right_center is not None:

            image_width = WIDTH
            middle_point = ((left_center[0] + right_center[0]) / 2, (left_center[1] + right_center[1]) / 2)
            center_x = image_width // 2
            self.error = round((center_x - middle_point[0]), 1)
            self.error_callback(self.error)

            # print(f"차선 중앙점: {middle_point}")
            print(f"오차(error): {self.error}")
            

        # for result in results:
        #     print(f"{result['name']} 감지됨, 신뢰도: {result['confidence']:.2f}")

        # 평균 신뢰도 계산
        avg_confidence = sum(result['confidence'] for result in results) / len(results)
        # print(f"평균 신뢰도: {avg_confidence:.2f}")

    def find_lane_centers(self, lane_masks):
        left_points = []
        right_points = []
        
        for mask in lane_masks:
            x_mean = np.mean(mask[:, 0])
            if x_mean < WIDTH/2:  # 이미지 중앙을 기준으로 왼쪽/오른쪽 구분
                left_points.append(mask)
            else:
                right_points.append(mask)
        
        left_center = None
        right_center = None

        if left_points:
            left_points_array = np.concatenate(left_points, axis=0)
            left_center = np.mean(left_points_array, axis=0)

        if right_points:
            right_points_array = np.concatenate(right_points, axis=0)
            right_center = np.mean(right_points_array, axis=0)
        
        return left_center, right_center


    def update_object_list(self, current_objects):
        """
        Update the list of objects which have been detected in the current frame.

        Args:
            current_objects (list): List of objects detected in the current frame.

        This function updates the list of objects which have been detected in the current frame.
        It adds any new objects to the list, and removes any objects that are no longer detected.
        """
        for obj in current_objects:
            if obj not in self.newlist:
                self.newlist.append(obj)

        for obj in self.newlist[:]:
            if obj not in current_objects:
                self.newlist.remove(obj)
        for obj in current_objects:
            if obj not in self.newlist:
                self.newlist.append(obj)

        for obj in self.newlist[:]:
            if obj not in current_objects:
                self.newlist.remove(obj)
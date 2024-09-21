import sys
import os
import cv2
import base64
import numpy as np
import time
from flask import Flask, jsonify

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '../../..')
sys.path.append(relative_path)

from Intelligence_Vehicle_Service.IVService import IVService
from Intelligence_Vehicle_Communicator.Flask.FlaskCummunicator import FlaskClient
from lane_detector import LaneDetector
from Intelligence_Vehicle_Service.Processor.LaneProcessor import LaneProcessor

app = Flask(__name__)

clients = {
    "Lane": 5001,
    "Obstacle": 5002,
    "DB": 5003,
    "Service": 5004
}

def ndarray_to_base64(img_array):
    _, buffer = cv2.imencode('.jpg', img_array)
    return base64.b64encode(buffer).decode('utf-8')

# results를 JSON 직렬화 가능하도록 변환하는 함수 추가
def convert_results_to_dict(results):
    if hasattr(results, '__dict__'):
        return results.__dict__  # 객체의 속성을 딕셔너리로 변환
    return results  # 이미 딕셔너리인 경우 그대로 반환

@app.route('/get_image')
def get_image():
    # LaneDetector 인스턴스를 생성하고 결과를 가져옵니다
    lane_detector = LaneDetector(model_path='Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                                 video_path='Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')
    
    # 비디오 처리 및 결과 전송
    for image, results in lane_detector.start_detect_result():
        img_base64 = ndarray_to_base64(image)  # 이미지를 base64로 변환
        lane_results = convert_results_to_dict(results)  # results 변환
        
        return jsonify({
            "lane_image": img_base64,  # base64로 변환된 이미지
            "lane_results": lane_results  # 변환된 결과
        })

if __name__ == "__main__":
    service = IVService()
    client = FlaskClient(client_id="Lane", port=clients["Lane"])
    client.set_callback(service.handle_receive_http_data)

    while True:
        if client.is_port_open(host='localhost', port=clients["Service"]):
            break
        print("Waiting for a server response.")
        time.sleep(1)

    lane_detector = LaneDetector(model_path='Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                                 video_path='Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

    lane_processor = LaneProcessor(model_path='Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt')

    # 비디오 처리 및 결과 전송
    # for image, results in lane_detector.get_results():
    #     lane_data = {
    #         "lane_image": ndarray_to_base64(image),  # 이미지를 base64로 변환
    #         "lane_results": convert_results_to_dict(results)  # results 변환
    #     }
    #     client.send_data(f"http://localhost:{clients['Service']}", "lane", {"data": lane_data})



    for results in lane_detector.start_detect_result():
        lane_data = {
            # "lane_results": convert_results_to_dict(results)
            "lane_masks": jsonify(results[0].masks)  # results 변환
            # "class_ids": results[0].boxes.cls
        }
        
        print(type(results[0]))

        client.send_data(f"http://localhost:{clients['Service']}", "lane", {"data": lane_data})

    cv2.destroyAllWindows()
    app.run(debug=True)

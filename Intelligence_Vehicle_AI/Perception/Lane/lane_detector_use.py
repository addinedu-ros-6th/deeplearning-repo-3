# 사용 예시
from lane_detector import LaneDetector

detector = LaneDetector('Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                         'Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

for error_value, stop_line_value in detector.process_video():
    print(f"Error: {error_value}, Stop Line Flag: {stop_line_value}")
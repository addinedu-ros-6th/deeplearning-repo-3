from lane_detector import LaneDetector

detector = LaneDetector('/home/heechun/dev_ws/deeplearning-repo-3/Intelligence_Vehicle_AI/Perception/Lane/best_v8n_seg.pt',
                         '/home/heechun/dev_ws/deeplearning-repo-3/Intelligence_Vehicle_AI/Dataset/Lane_dataset/30_only_lane_video.mp4')

detector.process_video()

# error 값과 stop_line_flag 값 가져오기
error_value = detector.get_error()
stop_line_value = detector.get_stop_line_flag()

print(f"Error: {error_value}, Stop Line Flag: {stop_line_value}")

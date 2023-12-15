import cv2
import argparse
import numpy as np
import os
import os.path as osp


def display_markers_on_frame(frame, markers, video_duration):
	height, width, _ = frame.shape
	marker_bar_height = int(height * 0.1)
	marker_bar = np.zeros((marker_bar_height, width, 3), dtype=np.uint8)

	for marker in markers:
		start_x = int(marker[0] * width / video_duration)
		end_x = int(marker[1] * width / video_duration)

		cv2.line(marker_bar, (start_x, 0), (start_x, marker_bar_height), (0, 255, 0), 2)
		if end_x > 0:
			cv2.line(marker_bar, (end_x, 0), (end_x, marker_bar_height), (0, 0, 255), 2)

	frame[:marker_bar_height, :] = marker_bar
	return frame


def video_manual_cut(video_name):
	markers = []
	cap = cv2.VideoCapture(video_name)
	fps = int(cap.get(cv2.CAP_PROP_FPS))
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # / cap.get(cv2.CAP_PROP_FPS)

	print(f"{fps=}")
	for fid in range(length):
		if fid % fps != 0:
			continue

		ret, frame = cap.read()
		if not ret:
			break
		frame = display_markers_on_frame(frame, markers, video_duration)
		cv2.imshow('Video Frame', frame)

		key = cv2.waitKey(1000 // fps) & 0xFF
		if key == ord('s'):
			current_time = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
			cur_sec = round(current_time / fps)
			print(f"Start time: {cur_sec} s")
			if len(markers) == 0 or markers[-1][-1] > 0:
				markers.append([cur_sec, 0])
			else:
				markers[-1][0] = cur_sec

		elif key == ord('e'):
			end_time = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
			end_sec = round(end_time / fps)
			markers[-1][-1] = end_sec
			print(f"End time: {end_sec} s")
			print(f"=> Pair: {markers[-1]}")
		elif key == ord('q'):
			break

	return markers



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--video', type=str, help='path to original video')
	parser.add_argument("--output", type=str, help='output folder to store markers')
	args = parser.parse_args()

	video_path = args.video
	markers = video_manual_cut(video_path)
	video_noex = osp.basename(video_path).split(".")[0]
	store_folder = args.output
	os.makedirs(store_folder, exist_ok=True)
	filename = osp.join(store_folder, f"cut_{video_noex}.txt")
	with open(filename, 'w') as f:
		for marker in markers:
			f.write(f"{marker[0]}, {marker[1]}\n")


if __name__ == "__main__":
	main()
import cv2
import argparse
import time
import os

class VideoPlayer:

	def __init__(self, video_path, video_speed, fps, playback_speed, save_location=None):
		self.cap = cv2.VideoCapture(video_path)
		self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
		self.fps = fps
		self.vid_time_per_frame = 1/self.fps
		self.real_time_per_frame = self.vid_time_per_frame * video_speed
		self.real_duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) * self.real_time_per_frame

		self.is_paused = False
		self.frame_num = 0
		
		self.speed = video_speed * playback_speed
		self.wait_time = (1/self.speed) * self.vid_time_per_frame

		self.save_location = save_location

	def play(self):
		while True:
			ret, frame = self.cap.read()
			if not ret:
				break

			self.display_info(frame)

			if self.is_paused:
				key = cv2.waitKey() & 0xFF
				if key == ord(' '):
					self.is_paused = False
				elif key == ord('a') and self.frame_num > 0:
					self.frame_num -= 1
					self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
					ret, frame = self.cap.read()
					self.display_info(frame)
					cv2.imshow('Video', cv2.resize(frame, (1280, int(frame.shape[0]*1280/frame.shape[1])), interpolation=cv2.INTER_CUBIC))
				elif key == ord('d'):
					self.frame_num += 1
					self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
					ret, frame = self.cap.read()
					self.display_info(frame)
					cv2.imshow('Video', cv2.resize(frame, (1280, int(frame.shape[0]*1280/frame.shape[1])), interpolation=cv2.INTER_CUBIC))
				elif key == ord('\r'):
					self.save_frame(frame)
				elif key == ord('q'):
					break
			else:
				self.frame_num += 1
				key = cv2.waitKey(1) & 0xFF
				if key == ord(' '):
					self.is_paused = True
				elif key == ord('q'):
					break
				
				cv2.imshow('Video', cv2.resize(frame, (1280, int(frame.shape[0]*1280/frame.shape[1])), interpolation=cv2.INTER_CUBIC))
				time.sleep(self.wait_time)

		self.cap.release()
		cv2.destroyAllWindows()

	def display_info(self, frame):
		real_time = self.frame_num * self.real_time_per_frame

		real_time_str = f"Real-time: {real_time:.4f} seconds/{self.real_duration:.4f} seconds"
		frame_info_str = f"Frame: {self.frame_num}/{self.total_frames}"

		cv2.putText(frame, real_time_str, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
				   1.5, (255, 255, 255), 3)
		cv2.putText(frame, frame_info_str, (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
				   1.5, (255, 255, 255), 3)

	def save_frame(self, frame):
		if self.save_location is None:
			print("No save location specified!")
			return
		real_time = self.frame_num * self.real_time_per_frame
		filename = f"{self.save_location}/frame_{self.frame_num}_time_{real_time:.4f}.png"
		cv2.imwrite(filename, frame)
		print(f"Frame saved as {filename}")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Video player for analysis of experiment videos")

	parser.add_argument("-video_path", type=str, required=True, help="Path to video file")
	parser.add_argument("-video_speed", type=float, default=1.0, help="Speed of video (0.25, 1.0, 3.0, etc.)")
	parser.add_argument("-fps", type=int, default=30, help="Frames per second")
	parser.add_argument("-playback_speed", type=float, default=1.0, help="Playback speed (0.25, 1.0, 3.0, etc.)")
	parser.add_argument("-save_location", type=str, default="", help="Location to save frames")

	args = parser.parse_args()

	video_path = args.video_path
	video_speed = args.video_speed
	fps = args.fps
	playback_speed = args.playback_speed
	save_location = args.save_location
	if save_location == "":
		save_location = os.path.dirname(video_path) + "/frames"
		if not os.path.exists(save_location):
			os.makedirs(save_location)
	
	player = VideoPlayer(video_path, video_speed, fps, playback_speed, save_location)
	player.play()

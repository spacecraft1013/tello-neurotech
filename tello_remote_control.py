from djitellopy import Tello
import threading
import keyboard
import cv2

SPEED = 10
TICKSPEED = 0.05
DRY_RUN = True

class LiveStream:
    def __init__(self, tello):
        self.frame_read = tello.get_frame_read()
        self.keepalive = True
        self.data_writers = [
            tello.get_xyz_speed,
            tello.get_yaw,
            tello.get_pitch,
            tello.get_roll,
            tello.get_battery,
            tello.get_barometer,
            tello.get_distance_tof,
            tello.get_highest_temperature,
            tello.get_flight_time
        ]
    
    @staticmethod
    def draw_text(image, text, row):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_size = 24
        font_color = (255,255,255)
        bg_color = (0,0,0)
        d = 2
        height, width = image.shape[:2]
        left_mergin = 10
        if row < 0:
            pos =  (left_mergin, height + font_size * row + 1)
        else:
            pos =  (left_mergin, font_size * (row + 1))
        cv2.putText(image, text, pos, font, font_scale, bg_color, 6)
        cv2.putText(image, text, pos, font, font_scale, font_color, 1)

    def prepare_image(self):
        frame = self.frame_read.frame
        for i, writer in enumerate(self.data_writers):
            self.draw_text(frame, f'{writer.__name__.replace("get_", "")}: {writer()}', 0-i)
        return frame
        
    def stream(self):
        while self.keepalive:
            cv2.imshow("Live Stream", self.prepare_image())
            time.sleep(TICKSPEED)


class Victim:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.set_speed(SPEED)
        self.tello.set_video_fps(Tello.FPS_30)
        self.tello.set_video_resolution(Tello.RESOLUTION_720P)
        self.tello.set_video_bitrate(Tello.BITRATE_5MBPS)

        self.tello.streamon()
        self.livestream = LiveStream(self.tello)
        self.stream_thread = threading.Thread(self.livestream.stream)
        self.active = True
        self.DIE = False

    def KILL_YOURSELF(self):
        self.tello.emergency()
        self.DIE = True

    def run(self):
        self.stream_thread.start()
        while not self.DIE:
            keyboard.on_press_key("k", self.KILL_YOURSELF)

            if not DRY_RUN and keyboard.is_pressed('t'):
                self.active = True
                self.tello.takeoff()

            if keyboard.is_pressed('l'):
                self.tello.land()
                break

            if not self.active:
                time.sleep(TICKSPEED)
                continue

            for_back_velocity = 0
            left_right_velocity = 0
            up_down_velocity = 0
            yaw_velocity = 0

            if keyboard.is_pressed('w+space'):
                if not DRY_RUN:
                    self.tello.flip_forward()
                else:
                    print('flip_forward')
                time.sleep(TICKSPEED)
                continue
            if keyboard.is_pressed('s+space'):
                if not DRY_RUN:
                    self.tello.flip_back()
                else:
                    print('flip_back')
                time.sleep(TICKSPEED)
                continue
            if keyboard.is_pressed('a+space'):
                if not DRY_RUN:
                    self.tello.flip_left()
                else:
                    print('flip_left')
                time.sleep(TICKSPEED)
                continue
            if keyboard.is_pressed('d+space'):
                if not DRY_RUN:
                    self.tello.flip_right()
                else:
                    print('flip_right')
                time.sleep(TICKSPEED)
                continue

            if keyboard.is_pressed('space'):
                up_down_velocity += SPEED
            if keyboard.is_pressed('ctrl'):
                up_down_velocity -= SPEED

            if keyboard.is_pressed('w'):
                for_back_velocity += SPEED
            if keyboard.is_pressed('s'):
                for_back_velocity -= SPEED
            if keyboard.is_pressed('a'):
                left_right_velocity -= SPEED
            if keyboard.is_pressed('d'):
                left_right_velocity += SPEED
            if keyboard.is_pressed('q'):
                yaw_velocity -= SPEED
            if keyboard.is_pressed('e'):
                yaw_velocity += SPEED

            if DRY_RUN:
                print(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
            else:
                self.tello.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)

        self.tello.land()
        self.tello.end()
        self.livestream.keepalive = False
        self.stream_thread.join()
        self.tello.streamoff()



if __name__ == "__main__":
    victim = Victim()
    victim.run()

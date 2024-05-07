import RubiksDetection.rpd.filtering as filtering
import RubiksDetection.rpd.viewport_properties as viewport_properties

import cv2 as cv
import numpy as np
import logging

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import RubiksDetection.rpd.viewport_properties as vp

class RubikCamera(Image):
    """Camera widget running rubik face detection.

    Displays the camera view with added debug information.
    """

    def __init__(self, rotated: bool, fps, debug_frame, on_new_frame,  **kwargs):
        super(RubikCamera, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.on_capture_reset()

        self.display_mode = "Original"
        self.display_mirror = False
        self.display_rotated = rotated

        self.on_new_frame = on_new_frame
        self.debugframe = debug_frame

        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        """Update."""
        ret, frame = self.capture.read()
        if frame is None:
            logging.fatal("frame is None")
        # else:
            # logging.info(f"Got frame({ret}): {frame.shape}")
        if ret:
            if self.display_rotated:
                frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)

            frame = cv.resize(frame, (viewport_properties.WIDTH, viewport_properties.HEIGHT))

            self.on_new_frame(frame)

            #  Display frame
            if self.display_mode == "Contours":
                frame = np.zeros((viewport_properties.HEIGHT, viewport_properties.WIDTH, 3), np.uint8)
            if self.display_mode == "Original":
                pass
            if self.display_mode == "Filtered":
                frame = filtering.amax_adaptive_filter(frame)
                frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)

            if self.display_mirror:
                frame = cv.flip(frame, 1)
            frame = self.debugframe(frame, self.display_mirror)
            # convert frame to rgb
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # convert it to texture
            frame = cv.flip(frame, 0)
            buf = frame.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            # display image from the texture
            self.texture = image_texture

    def change_display_mode(self, mode: str):
        self.display_mode = mode

    def on_pause(self):
        return True

    def on_stop(self):
        logging.info("Releasing camera")
        self.capture.release()

    def on_resume(self):
        self.on_capture_reset()

    def on_capture_reset(self):
        self.capture = cv.VideoCapture(0)
        if not self.capture.isOpened():
            logging.fatal("Cam is not opened")
        logging.info(f"Camera format is: {self.capture.get(cv.CAP_PROP_FORMAT)}")
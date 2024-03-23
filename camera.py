import RubiksDetection.rpd.features as features
import RubiksDetection.rpd.filtering as filtering
import RubiksDetection.rpd.viewport_properties as viewport_properties
import RubiksDetection.rpd.detection_engine as rpd
import cv2 as cv
import numpy as np
import logging

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.utils import platform

import RubiksDetection.rpd.viewport_properties as vp
import RubiksDetection.rpd.labeling as rbs

class RubikCamera(Image):
    """Camera widget running rubik face detection.

    Displays the camera view with added debug information.
    """

    def __init__(self, capture, fps, **kwargs):
        super(RubikCamera, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.draw_orientation = False
        self.draw_contours = True
        self.draw_face = True

        self.capture = capture
        self.display_mode = "Original"
        self.detection_engine = rpd.DetectionEngine()
        self.state = rbs.LabelingEngine()
        # Don't havea better place to put this, but the android camera is rotated 90 degrees so viewport properties need to be swapped
        if platform == 'android':
            vp.WIDTH, vp.HEIGHT = vp.HEIGHT, vp.WIDTH
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        """Update."""
        ret, frame = self.capture.read()
        if frame is None:
            logging.fatal("frame is None")
        # else:
            # logging.info(f"Got frame({ret}): {frame.shape}")
        if ret:
            # rotate 90 clockwise if on android
            if platform == 'android':
                frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)

            frame = cv.resize(frame, (viewport_properties.WIDTH, viewport_properties.HEIGHT))

            self.detection_engine.process_frame(frame)

            #  Display frame
            if self.display_mode == "Contours":
                frame = np.zeros((viewport_properties.HEIGHT, viewport_properties.WIDTH, 3), np.uint8)
            if self.display_mode == "Original":
                pass
            if self.display_mode == "Filtered":
                frame = filtering.canny_amax_adaptive_filter(frame)
                frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)

            frame = self.detection_engine.debug_frame(frame, draw_orientation= self.draw_orientation, draw_contours=self.draw_contours, draw_face=self.draw_face)
            # convert frame to rgb
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # convert it to texture
            buf1 = cv.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            # display image from the texture
            self.texture = image_texture

    def change_display_mode(self, mode: str):
        self.display_mode = mode

    def on_capture(self):
        logging.info(f"Capturing face: {len(self.state.face_data)}")
        if(self.detection_engine.last_face is not None):
            self.state.consume_face(self.detection_engine.last_face)
            self.detection_engine.last_face = None
        if self.state.is_complete():
            self.state.fit()
            img = self.state.debug_image()
            cv.imwrite("rubik_state.png", img)
            print(self.state.stateString())
            self.state.reset()

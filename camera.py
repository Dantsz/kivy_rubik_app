import RubiksDetection.rpd.filtering as filtering
import RubiksDetection.rpd.viewport_properties as viewport_properties
import RubiksDetection.rpd.solve as solve

from RubiksDetection.rpd.detection_engine import DetectionEngine
from RubiksDetection.rpd.labeling import LabelingEngine
from RubiksDetection.rpd.solution_display import SolutionDisplayEngine

import cv2 as cv
import numpy as np
import logging

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.utils import platform

import RubiksDetection.rpd.viewport_properties as vp

class RubikCamera(Image):
    """Camera widget running rubik face detection.

    Displays the camera view with added debug information.
    """

    def __init__(self, capture, fps, detection_engine: DetectionEngine, labeling_engine: LabelingEngine, solution_engine: SolutionDisplayEngine, **kwargs):
        super(RubikCamera, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.draw_orientation = False
        self.draw_contours = True
        self.draw_face = True
        self.draw_avg_color = False
        self.draw_coordinates = False

        self.capture = capture
        self.display_mode = "Original"

        self.detection_engine = detection_engine
        self.state = labeling_engine
        self.solution_display = solution_engine

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

            frame = self.detection_engine.debug_frame(frame, draw_orientation= self.draw_orientation, draw_contours=self.draw_contours, draw_face=self.draw_face, draw_avg_color=self.draw_avg_color, draw_coordinates=self.draw_coordinates)
            if self.solution_display.ready() and self.detection_engine.last_frame_detected_face():
                frame = self.solution_display.display_solution(frame, self.state.color_centers)
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

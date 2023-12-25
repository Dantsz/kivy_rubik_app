from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
import RubiksDetection.rpd.features as features
import RubiksDetection.rpd.filtering as filtering
import RubiksDetection.rpd.viewport_properties as viewport_properties
import cv2 as cv
import numpy as np
import logging

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False

        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if frame is None:
            logging.fatal("frame is None")
        else:
            logging.info(f"Got frame({ret}): {frame.shape}")
        if ret:
            #rotate 90 clockwise if on android
            if platform == 'android':
                frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)

            img = frame.copy()
            frame = filtering.canny_amax_adaptive_filter(frame)
            contours, hierarchy = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            contours = features.contours_filter_small_area(contours, viewport_properties.FEATURES_FILTER_MIN_AREA)
            contours = features.contours_filter_solidity(contours, viewport_properties.FEATURES_FILTER_SOLIDITY)
            contours = features.contours_filter_positional_2(contours, viewport_properties.FEATURES_FILTER_POSITIONAL_2_DISTANCE)
            contours = features.approx_polygon_from_contour(contours)
            img_2 = cv.drawContours(img, contours, -1, (0,255,0), 3)


            frame = img_2
            # convert frame to rgb
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # convert it to texture
            buf1 = cv.flip(frame, 0)
            buf= buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            # display image from the texture
            self.texture = image_texture


class CamApp(App):
    def build(self):

        self.capture = cv.VideoCapture(0)
        if not self.capture.isOpened():
            logging.fatal("Cam is not opened")
        logging.info(f"Camera format is: {self.capture.get(cv.CAP_PROP_FORMAT)}")
        self.box_layout = BoxLayout(orientation='vertical')

        my_camera = KivyCamera(capture=self.capture, fps=30)
        self.box_layout.add_widget(my_camera)

        return self.box_layout

    def on_stop(self):
        #without this, app will not exit even if the window is closed
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.utils import platform
import RubiksDetection.rpd.features as features
import RubiksDetection.rpd.filtering as filtering
import cv2 as cv
import numpy as np
import logging
from camera import KivyCamera
class CamApp(App):
    def build(self):
        self.capture = cv.VideoCapture(0)
        if not self.capture.isOpened():
            logging.fatal("Cam is not opened")
        logging.info(f"Camera format is: {self.capture.get(cv.CAP_PROP_FORMAT)}")
        self.root = FloatLayout()

        self.camera = KivyCamera(capture=self.capture, fps=30)
        self.root.add_widget(self.camera)

        setting_layout = BoxLayout(orientation='horizontal',size_hint=(None, None), size=(200, 50),
                                 pos_hint={'right': 1, 'bottom': 1})

        settings_button = Button(text='Settings')
        settings_button.bind(on_release=self.on_settings_button_press)

        image_spinner = Spinner(text="Display mode", values=("Original","Filtered","Contours"))
        image_spinner.bind(text=self.on_display_mode_change)
        setting_layout.add_widget(settings_button)
        setting_layout.add_widget(image_spinner)
        self.root.add_widget(setting_layout)

        return self.root

    def on_settings_button_press(self, instance):
        pass

    def on_display_mode_change(self, instance, value):
        print("Display mode changed to: " + value)
        self.camera.change_display_mode(value)



    def on_stop(self):
        #without this, app will not exit even if the window is closed
        logging.info("Releasing camera")
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.utils import platform


import cv2 as cv
import logging
import asyncio

from camera import RubikCamera

class CamApp(App):
    """Main application."""

    def build(self):
        """Build a camera app."""
        self.capture = cv.VideoCapture(0)
        if not self.capture.isOpened():
            logging.fatal("Cam is not opened")
        logging.info(f"Camera format is: {self.capture.get(cv.CAP_PROP_FORMAT)}")
        self.root = FloatLayout()

        self.camera = RubikCamera(capture=self.capture, fps=15)

        self.root.add_widget(self.camera)

        setting_layout = BoxLayout(orientation='vertical',
                                   size_hint=(None, None),
                                   size=(100, 50),
                                   pos_hint={'right': 1, 'top': 1})

        image_spinner = Spinner(text="Display mode",
                                values=("Original", "Filtered", "Contours"))
        image_spinner.bind(text=self.on_display_mode_change)

        settings_dropdown = DropDown()
        contours_button = Button(text='Contours', size_hint_y=None, height=44)
        contours_button.bind(on_release=self.on_contours_button_press)
        settings_dropdown.add_widget(contours_button)

        face_button = Button(text='Face', size_hint_y=None, height=44)
        face_button.bind(on_release=self.on_face_button_press)
        settings_dropdown.add_widget(face_button)

        orientation_button = Button(text='Orientation', size_hint_y=None, height=44)
        orientation_button.bind(on_release=self.on_orientation_button_press)
        settings_dropdown.add_widget(orientation_button)



        settings_button = Button(text='Settings')
        settings_button.bind(on_release=settings_dropdown.open)

        setting_layout.add_widget(settings_button)
        setting_layout.add_widget(image_spinner)

        self.root.add_widget(setting_layout)

        capture_button = Button(text='Capture',
                                size_hint=(None, None),
                                size=(100, 50),
                                pos_hint={'center_x': 0.5, 'center_y': 0.10})
        capture_button.bind(on_release=self.on_capture_button_press)
        self.root.add_widget(capture_button)

        return self.root

    def on_settings_button_press(self, instance):
        pass

    def on_display_mode_change(self, instance, value):
        print("Display mode changed to: " + value)
        self.camera.change_display_mode(value)

    def on_capture_button_press(self, instance):
        self.camera.on_capture()

    def on_orientation_button_press(self, instance):
        self.camera.draw_orientation = not self.camera.draw_orientation

    def on_contours_button_press(self, instance):
        self.camera.draw_contours = not self.camera.draw_contours

    def on_face_button_press(self, instance):
        self.camera.draw_face = not self.camera.draw_face

    def on_stop(self):
        # without this, app will not exit even if the window is closed
        logging.info("Releasing camera")
        self.capture.release()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        CamApp().async_run()
    )
    loop.close()
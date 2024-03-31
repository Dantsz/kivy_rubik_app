from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.utils import platform, get_color_from_hex


import cv2 as cv
import logging

import asyncio


from RubiksDetection.rpd.detection_engine import DetectionEngine
from RubiksDetection.rpd.labeling import LabelingEngine

from camera import RubikCamera
import app_state

def condition_color(condition: bool) -> str:
    """Return a color based on a condition."""
    return get_color_from_hex("#00FF00") if condition else get_color_from_hex("#FF0000")

class CamApp(App):
    """Main application."""

    def build(self):
        """Build a camera app."""
        self.capture = cv.VideoCapture(0)
        if not self.capture.isOpened():
            logging.fatal("Cam is not opened")
        logging.info(f"Camera format is: {self.capture.get(cv.CAP_PROP_FORMAT)}")
        self.root = FloatLayout()

        self.detection_engine = DetectionEngine()
        self.labeling_engine = LabelingEngine()
        self.camera = RubikCamera(capture=self.capture, detection_engine=self.detection_engine, labeling_engine=self.labeling_engine, fps=15)
        self.state = app_state.RubikDetectionState(self.detection_engine, self.labeling_engine)

        self.root.add_widget(self.camera)

        setting_layout = BoxLayout(orientation='vertical',
                                   size_hint=(None, None),
                                   size=(100, 50),
                                   pos_hint={'right': 1, 'top': 1})

        display_dropdown = self.build_display_dropdown()
        display_button = Button(text='Display')
        display_button.bind(on_release=display_dropdown.open)

        settings_dropdown = self.build_settings_dropdown()
        settings_button = Button(text='Settings')
        settings_button.bind(on_release=settings_dropdown.open)

        setting_layout.add_widget(display_button)
        setting_layout.add_widget(settings_button)

        self.root.add_widget(setting_layout)

        capture_layout = BoxLayout(orientation='horizontal',
                                      size_hint=(None, None),
                                      size=(100, 50),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.10})
        capture_button = Button(text='Capture',
                                size_hint=(None, None),
                                size=(100, 50))
        capture_button.bind(on_release=self.on_capture_button_press)
        capture_layout.add_widget(capture_button)

        reset_button = Button(text="Reset",
                                size_hint=(None, None),
                                size=(50, 50))
        reset_button.bind(on_release=self.on_reset)
        capture_layout.add_widget(reset_button)

        self.root.add_widget(capture_layout)

        return self.root

    def on_reset(self,instance):
        self.state.send('reset')

    def build_display_dropdown(self) -> DropDown:
        settings_dropdown = DropDown()
        contours_button = Button(text='Contours', size_hint_y=None, height=44)
        contours_button.bind(on_release=self.on_contours_button_press)
        contours_button.background_color = condition_color(self.camera.draw_contours)
        settings_dropdown.add_widget(contours_button)

        face_button = Button(text='Face', size_hint_y=None, height=44)
        face_button.bind(on_release=self.on_face_button_press)
        face_button.background_color = condition_color(self.camera.draw_face)
        settings_dropdown.add_widget(face_button)

        orientation_button = Button(text='Orientation', size_hint_y=None, height=44)
        orientation_button.bind(on_release=self.on_orientation_button_press)
        orientation_button.background_color = condition_color(self.camera.draw_orientation)
        settings_dropdown.add_widget(orientation_button)

        avg_color_button = Button(text='Avg Color', size_hint_y=None, height=44)
        avg_color_button.bind(on_release=self.on_avg_color_button_press)
        avg_color_button.background_color = condition_color(self.camera.draw_avg_color)
        settings_dropdown.add_widget(avg_color_button)

        coordinates_button = Button(text='Coordinates', size_hint_y=None, height=44)
        coordinates_button.bind(on_release=self.on_coordinates_button_press)
        coordinates_button.background_color = condition_color(self.camera.draw_coordinates)
        settings_dropdown.add_widget(coordinates_button)

        image_spinner = Spinner(text="Display mode",
                                values=("Original", "Filtered", "Contours"), size_hint_y=None, height=44)
        image_spinner.bind(text=self.on_display_mode_change)
        settings_dropdown.add_widget(image_spinner)

        return settings_dropdown

    def build_settings_dropdown(self) -> DropDown:
        settings_dropdown = DropDown()
        return settings_dropdown

    def on_settings_button_press(self, instance):
        pass

    def on_display_mode_change(self, instance, value):
        print("Display mode changed to: " + value)
        self.camera.change_display_mode(value)

    def on_capture_button_press(self, instance):
        self.state.send('capture')

    def on_orientation_button_press(self, instance):
        self.camera.draw_orientation = not self.camera.draw_orientation
        instance.background_color = condition_color(self.camera.draw_orientation)

    def on_contours_button_press(self, instance):
        self.camera.draw_contours = not self.camera.draw_contours
        instance.background_color = condition_color(self.camera.draw_contours)

    def on_face_button_press(self, instance):
        self.camera.draw_face = not self.camera.draw_face
        instance.background_color = condition_color(self.camera.draw_face)

    def on_avg_color_button_press(self, instance):
        self.camera.draw_avg_color = not self.camera.draw_avg_color
        instance.background_color = condition_color(self.camera.draw_avg_color)

    def on_coordinates_button_press(self, instance):
        self.camera.draw_coordinates = not self.camera.draw_coordinates
        instance.background_color = condition_color(self.camera.draw_coordinates)

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
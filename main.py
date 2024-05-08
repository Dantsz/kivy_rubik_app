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

from RubiksDetection.detection_engine import DetectionEngine
from RubiksDetection.labeling import LabelingEngine
from RubiksDetection.solution_display import SolutionDisplayEngine
from RubiksDetection import viewport_properties as vp

from camera import RubikCamera
import app_state

# Don't have better place to put this, but the android camera is rotated 90 degrees so viewport properties need to be swapped
if platform == 'android':
    vp.WIDTH, vp.HEIGHT = vp.HEIGHT, vp.WIDTH

def condition_color(condition: bool) -> str:
    """Return a color based on a condition."""
    return get_color_from_hex("#00FF00") if condition else get_color_from_hex("#FF0000")

class RubiksDetectionApp(App):
    """Main application."""

    def build(self):
        """Build a camera app."""

        self.detection_engine = DetectionEngine()
        self.labeling_engine = LabelingEngine()
        self.solution_display = SolutionDisplayEngine()
        # rotate 90 clockwise if on android
        if platform == 'android':
            rotated = True
        else:
            rotated = False
        self.camera = RubikCamera(on_new_frame=self.on_new_frame,rotated=rotated, debug_frame=self.debug_frame, fps=15)
        self.state = app_state.RubikDetectionState(self.detection_engine, self.labeling_engine, self.solution_display)

        self.keep_ratio = False
        self.draw_orientation = False
        self.draw_contours = True
        self.draw_face = True
        self.draw_avg_color = False
        self.draw_coordinates = False
        self.draw_solution = True
        self.draw_miniature = True

        self.root = FloatLayout()

        self.root.add_widget(self.camera)

        setting_layout = BoxLayout(orientation='horizontal',
                                   size_hint=(None, None),
                                   size=(200, 50),
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

    def on_pause(self):
        return self.camera.on_pause()

    def on_resume(self):
        self.camera.on_resume()

    def build_display_dropdown(self) -> DropDown:
        settings_dropdown = DropDown()
        contours_button = Button(text='Contours', size_hint_y=None, height=44)
        contours_button.bind(on_release=self.on_contours_button_press)
        contours_button.background_color = condition_color(self.draw_contours)
        settings_dropdown.add_widget(contours_button)

        face_button = Button(text='Face', size_hint_y=None, height=44)
        face_button.bind(on_release=self.on_face_button_press)
        face_button.background_color = condition_color(self.draw_face)
        settings_dropdown.add_widget(face_button)

        orientation_button = Button(text='Orientation', size_hint_y=None, height=44)
        orientation_button.bind(on_release=self.on_orientation_button_press)
        orientation_button.background_color = condition_color(self.draw_orientation)
        settings_dropdown.add_widget(orientation_button)

        avg_color_button = Button(text='Avg Color', size_hint_y=None, height=44)
        avg_color_button.bind(on_release=self.on_avg_color_button_press)
        avg_color_button.background_color = condition_color(self.draw_avg_color)
        settings_dropdown.add_widget(avg_color_button)

        coordinates_button = Button(text='Coordinates', size_hint_y=None, height=44)
        coordinates_button.bind(on_release=self.on_coordinates_button_press)
        coordinates_button.background_color = condition_color(self.draw_coordinates)
        settings_dropdown.add_widget(coordinates_button)

        miniature_button = Button(text='Miniature', size_hint_y=None, height=44)
        miniature_button.bind(on_release=self.on_miniature_button_press)
        miniature_button.background_color = condition_color(self.draw_miniature)
        settings_dropdown.add_widget(miniature_button)

        solution_button = Button(text='Solution', size_hint_y=None, height=44)
        solution_button.bind(on_release=self.on_solution_button_press)
        solution_button.background_color = condition_color(self.draw_solution)
        settings_dropdown.add_widget(solution_button)

        image_spinner = Spinner(text="Display mode",
                                values=("Original", "Filtered", "Contours"), size_hint_y=None, height=44)
        image_spinner.bind(text=self.on_display_mode_change)
        settings_dropdown.add_widget(image_spinner)

        return settings_dropdown

    def build_settings_dropdown(self) -> DropDown:
        settings_dropdown = DropDown()
        rotated_button = Button(text='Rotate', size_hint_y=None, height=44)
        rotated_button.bind(on_release=self.on_rotate_button_press)
        rotated_button.background_color = condition_color(self.camera.display_rotated)
        settings_dropdown.add_widget(rotated_button)

        mirror_button = Button(text='Mirror', size_hint_y=None, height=44)
        mirror_button.bind(on_release=self.on_mirror_button_press)
        mirror_button.background_color = condition_color(self.camera.display_mirror)
        settings_dropdown.add_widget(mirror_button)

        clustering_spinner = Spinner(text="Closest",
                                     values=("Closest", "KMeans"), size_hint_y=None, height=44)
        clustering_spinner.bind(text=self.on_clustering_change)
        settings_dropdown.add_widget(clustering_spinner)

        return settings_dropdown

    def on_settings_button_press(self, instance):
        pass

    def on_display_mode_change(self, instance, value):
        print("Display mode changed to: " + value)
        self.camera.change_display_mode(value)

    def on_clustering_change(self, instance, value):
        print("Clustering changed to: " + value)
        match value:
            case "Closest":
                self.labeling_engine.clusteting_method = 0
            case "KMeans":
                self.labeling_engine.clusteting_method = 1

    def on_capture_button_press(self, instance):
        self.state.send('capture')

    def on_orientation_button_press(self, instance):
        self.draw_orientation = not self.draw_orientation
        instance.background_color = condition_color(self.draw_orientation)

    def on_contours_button_press(self, instance):
        self.draw_contours = not self.draw_contours
        instance.background_color = condition_color(self.draw_contours)

    def on_face_button_press(self, instance):
        self.draw_face = not self.draw_face
        instance.background_color = condition_color(self.draw_face)

    def on_avg_color_button_press(self, instance):
        self.draw_avg_color = not self.draw_avg_color
        instance.background_color = condition_color(self.draw_avg_color)

    def on_coordinates_button_press(self, instance):
        self.draw_coordinates = not self.draw_coordinates
        instance.background_color = condition_color(self.draw_coordinates)

    def on_solution_button_press(self, instance):
        self.draw_solution = not self.draw_solution
        instance.background_color = condition_color(self.draw_solution)

    def on_miniature_button_press(self, instance):
        self.draw_miniature = not self.draw_miniature
        instance.background_color = condition_color(self.draw_miniature)

    def on_mirror_button_press(self, instance):
        self.camera.display_mirror = not self.camera.display_mirror
        instance.background_color = condition_color(self.camera.display_mirror)

    def on_rotate_button_press(self, instance):
        self.camera.display_rotated = not self.camera.display_rotated
        instance.background_color = condition_color(self.camera.display_rotated)

    def on_new_frame(self, frame):
        self.detection_engine.process_frame(frame)

    def debug_frame(self, frame, mirrored):
        frame = self.detection_engine.debug_frame(frame,
                                                    draw_orientation= self.draw_orientation,
                                                    draw_contours=self.draw_contours,
                                                    draw_face=self.draw_face,
                                                    draw_avg_color=self.draw_avg_color,
                                                    draw_coordinates=self.draw_coordinates,
                                                    draw_miniature=self.draw_miniature,
                                                    mirrored=mirrored)
        if self.detection_engine.last_face is not None and self.draw_solution:
            frame, _status = self.solution_display.display(frame, self.detection_engine.last_face, mirrored=mirrored)
        return frame

    def on_stop(self):
        # without this, app will not exit even if the window is closed
        self.camera.on_stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        RubiksDetectionApp().async_run()
    )
    loop.close()
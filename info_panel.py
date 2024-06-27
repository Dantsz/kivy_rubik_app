from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

class InfoPanel(ModalView):
    def __init__(self, **kwargs):
        super(InfoPanel, self).__init__(**kwargs)
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = True
        self.layout = GridLayout(cols=2, spacing=10)
        self.layout.orientation = 'lr-tb'
        self.add_widget(self.layout)

        self.key_time = Label(text="Time")
        self.layout.add_widget(self.key_time)
        self.value_time_label = Label()
        self.layout.add_widget(self.value_time_label)

        self.key_capture_label = Label(text="Captures")
        self.layout.add_widget(self.key_capture_label)
        self.value_capture_label = Label()
        self.layout.add_widget(self.value_capture_label)

        self.key_faces_label = Label(text="Captures with face")
        self.layout.add_widget(self.key_faces_label)
        self.value_faces_label = Label()
        self.layout.add_widget(self.value_faces_label)

        self.key_avg_contours_in_frames_with_faces_label = Label(text="Average contours in frames with face")
        self.layout.add_widget(self.key_avg_contours_in_frames_with_faces_label)
        self.value_avg_contours_in_frames_with_faces_label = Label()
        self.layout.add_widget(self.value_avg_contours_in_frames_with_faces_label)

        self.key_variance_contours_in_frames_with_faces_label = Label(text="Variance of contours in frames with face")
        self.layout.add_widget(self.key_variance_contours_in_frames_with_faces_label)
        self.value_variance_contours_in_frames_with_faces_label = Label()
        self.layout.add_widget(self.value_variance_contours_in_frames_with_faces_label)

        self.value_last_detection_time_label = Label(text="Last detection time")
        self.layout.add_widget(self.value_last_detection_time_label)
        self.value_last_detection_time_label = Label()
        self.layout.add_widget(self.value_last_detection_time_label)

        self.value_avg_detection_time_label = Label(text="Average detection time")
        self.layout.add_widget(self.value_avg_detection_time_label)
        self.value_avg_detection_time_label = Label()
        self.layout.add_widget(self.value_avg_detection_time_label)

        self.value_last_labeling_time_label = Label(text="Last labeling time")
        self.layout.add_widget(self.value_last_labeling_time_label)
        self.value_last_labeling_time_label = Label()
        self.layout.add_widget(self.value_last_labeling_time_label)

        self.value_avg_labeling_time_label = Label(text="Average labeling time")
        self.layout.add_widget(self.value_avg_labeling_time_label)
        self.value_avg_labeling_time_label = Label()
        self.layout.add_widget(self.value_avg_labeling_time_label)

        self.reset_button = Button(text="Reset")
        self.reset_button.bind(on_press=self.reset)
        self.layout.add_widget(self.reset_button)

        self.reset()
        Clock.schedule_interval(self.on_update_time_incremented, 1)

    def on_update_time_incremented(self, *args):
        self.value_time += 1
        self.value_time_label.text = str(self.value_time)

    def on_update_capture_incremented(self):
        self.value_capture += 1
        self.value_capture_label.text = str(self.value_capture)

    def on_update_faces_incremented(self, detected_contours: int):
        self.value_avg_contours_in_frames_with_faces *= self.value_faces
        self.value_faces += 1

        self.value_avg_contours_in_frames_with_faces += detected_contours
        self.value_square_sum_contours_in_frames_with_faces += detected_contours * detected_contours

        self.value_avg_contours_in_frames_with_faces /= self.value_faces
        self.value_variance_contours_in_frames_with_faces =  (self.value_square_sum_contours_in_frames_with_faces / self.value_faces) - (self.value_avg_contours_in_frames_with_faces * self.value_avg_contours_in_frames_with_faces)

        self.value_faces_label.text = str(self.value_faces)
        self.value_avg_contours_in_frames_with_faces_label.text = str(self.value_avg_contours_in_frames_with_faces)
        self.value_variance_contours_in_frames_with_faces_label.text = str(self.value_variance_contours_in_frames_with_faces)

    def on_update_last_detection_time(self, value):
        self.value_last_detection_time = value
        self.value_last_detection_time_label.text = str(self.value_last_detection_time)
        self.value_avg_detection_time = (self.value_avg_detection_time * (self.value_capture - 1) + self.value_last_detection_time) / self.value_capture
        self.value_avg_detection_time_label.text = str(self.value_avg_detection_time)

    def on_update_last_labeling_time(self, result: bool, value):
        if result:
            self.value_labelings += 1
            self.value_last_labeling_time = value
            self.value_last_labeling_time_label.text = str(self.value_last_labeling_time)
            self.value_avg_labeling_time = (self.value_avg_labeling_time * (self.value_labelings - 1) + self.value_last_labeling_time) / self.value_labelings
            self.value_avg_labeling_time_label.text = str(self.value_avg_labeling_time)

    def reset(self, instance=None):
        self.value_time = 0
        self.value_time_label.text = str(self.value_time)
        self.value_capture = 0
        self.value_capture_label.text = str(self.value_capture)
        self.value_faces = 0
        self.value_faces_label.text = str(self.value_faces)
        self.value_avg_contours_in_frames_with_faces = 0
        self.value_square_sum_contours_in_frames_with_faces = 0
        self.value_avg_contours_in_frames_with_faces_label.text = str(self.value_avg_contours_in_frames_with_faces)
        self.value_variance_contours_in_frames_with_faces = 0
        self.value_variance_contours_in_frames_with_faces_label.text = str(self.value_variance_contours_in_frames_with_faces)
        self.value_last_detection_time = 0
        self.value_last_detection_time_label.text = str(self.value_last_detection_time)
        self.value_avg_detection_time = 0
        self.value_avg_detection_time_label.text = str(self.value_avg_detection_time)
        self.value_labelings = 0
        self.value_last_labeling_time = 0
        self.value_last_labeling_time_label.text = str(self.value_last_labeling_time)
        self.value_avg_labeling_time = 0
        self.value_avg_labeling_time_label.text = str(self.value_avg_labeling_time)

    def on_update(self, dt):
        pass
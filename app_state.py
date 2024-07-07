import logging
from statemachine import StateMachine, State

from RubiksDetection.detection_engine import DetectionEngine
from RubiksDetection.labeling import LabelingEngine
from RubiksDetection.solution_display import SolutionDisplayEngine
import RubiksDetection.solve as solve

import cv2 as cv
class RubikDetectionState(StateMachine):
    """The state machine for the Rubik's Cube detection application"""
    WhiteFaceReading = State(initial=True)
    RedFaceRead = State()
    GreenFaceRead = State()
    YellowFaceRead = State()
    OrangeFaceRead = State()
    BlueFaceRead = State()

    DoneCubeCapture = State()
    InconsistentCube = State()

    DisplayState = State()
    EndDisplayState = State()

    capture = (
        WhiteFaceReading.to(RedFaceRead)
        | RedFaceRead.to(GreenFaceRead)
        | GreenFaceRead.to(YellowFaceRead)
        | YellowFaceRead.to(OrangeFaceRead)
        | OrangeFaceRead.to(BlueFaceRead)
        | BlueFaceRead.to(DoneCubeCapture)
    )

    reset = (
        WhiteFaceReading.to(WhiteFaceReading)
        | RedFaceRead.to(WhiteFaceReading)
        | GreenFaceRead.to(WhiteFaceReading)
        | YellowFaceRead.to(WhiteFaceReading)
        | OrangeFaceRead.to(WhiteFaceReading)
        | BlueFaceRead.to(WhiteFaceReading)
        | DisplayState.to(WhiteFaceReading)
        | EndDisplayState.to(WhiteFaceReading)
        | InconsistentCube.to(WhiteFaceReading)
    )

    inconsistencyDetected = (
        DoneCubeCapture.to(InconsistentCube)
    )

    startDisplay = (
        DoneCubeCapture.to(DisplayState)
    )

    solved = (
        DisplayState.to(EndDisplayState)
    )

    def on_capture(self):
        logging.info(f"Capturing face: {len(self.labeling_engine.face_data)}")
        face = self.detection_engine.pop_face()
        if(face is not None):
            self.labeling_engine.consume_face(face)
        if self.labeling_engine.is_complete():
            try:
                self.labeling_engine.fit()
                logging.info(f"Cube is {self.labeling_engine.stateString()}")
                moves = solve.solve(self.labeling_engine.state())
                self.__signal_labeling_result(True)
                print(moves)
                print(self.labeling_engine.color_centers)
                self.__setup_solution_display(moves)
            except ValueError as e:
                logging.warning(f"Cube is inconsistent: {e}")
                self.__setup_solution_display_fail()
                self.__signal_labeling_result(False)
            finally:
                # img = self.labeling_engine.debug_image_2d()
                # cv.imwrite("rubik_state_2d.png", img)

                # img = self.labeling_engine.debug_image_3d()
                # cv.imwrite("rubik_state_3d.png", img)
                pass

    def __setup_solution_display_fail(self):
       self.solution_engine.display_errors = True
       def __on_start_display_error():
            self.send('inconsistencyDetected')
       self.solution_engine.on_solution_start =  __on_start_display_error

    def __setup_solution_display(self, moves: list[solve.Move]):
            def __on_start_display():
                self.send('startDisplay')
            def __on_done_display():
                self.send('solved')

            self.solution_engine.on_solution_start = __on_start_display
            self.solution_engine.on_solution_done = __on_done_display
            self.solution_engine.consume_solution(self.labeling_engine.color_centers, self.labeling_engine.state(), moves)


    def on_enter_WhiteFaceReading(self):
        logging.info(f"AppState: Reading white face")
    def on_enter_RedFaceRead(self):
        logging.info("AppState: Reading red face")
    def on_enter_GreenFaceRead(self):
        logging.info("AppState: Reading green face")
    def on_enter_YellowFaceRead(self):
        logging.info("AppState: Reading yellow face")
    def on_enter_OrangeFaceRead(self):
        logging.info("AppState: Reading orange face")
    def on_enter_BlueFaceRead(self):
        logging.info("AppState: Reading blue face")

    def on_reset(self):
        logging.info("AppState: Resetting state")
        self.labeling_engine.reset()
        self.solution_engine.reset()

    def after_transition(self):
        # img_path = "state_machine.png"
        # self._graph().write_png(img_path)
        pass

    def __signal_labeling_result(self, result):
        if self.__report_labeling_result is not None:
            self.__report_labeling_result(result)

    def __init__(self, detection_engine: DetectionEngine, labeling_engine: LabelingEngine, solution_display_engine: SolutionDisplayEngine, report_labeling_result: callable = None):
        super().__init__()
        self.detection_engine = detection_engine
        self.labeling_engine = labeling_engine
        self.__report_labeling_result = report_labeling_result
        self.solution_engine = solution_display_engine
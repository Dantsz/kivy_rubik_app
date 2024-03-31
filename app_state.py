import logging
from statemachine import StateMachine, State

from RubiksDetection.rpd.detection_engine import DetectionEngine
from RubiksDetection.rpd.labeling import LabelingEngine


class RubikDetectionState(StateMachine):
    """The state machine for the Rubik's Cube detection application"""
    WhiteFaceReading = State(initial=True)
    RedFaceRead = State()
    GreenFaceRead = State()
    YellowFaceRead = State()
    OrangeFaceRead = State()
    BlueFaceRead = State()

    doneCubeCapture = State()

    capture = (
        WhiteFaceReading.to(RedFaceRead)
        | RedFaceRead.to(GreenFaceRead)
        | GreenFaceRead.to(YellowFaceRead)
        | YellowFaceRead.to(OrangeFaceRead)
        | OrangeFaceRead.to(BlueFaceRead)
        | BlueFaceRead.to(doneCubeCapture)
    )

    reset = (
        WhiteFaceReading.to(WhiteFaceReading)
        | RedFaceRead.to(WhiteFaceReading)
        | GreenFaceRead.to(WhiteFaceReading)
        | YellowFaceRead.to(WhiteFaceReading)
        | OrangeFaceRead.to(WhiteFaceReading)
        | BlueFaceRead.to(WhiteFaceReading)
        | doneCubeCapture.to(WhiteFaceReading)
    )

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

    def after_transition(self):
        img_path = "readme_trafficlightmachine.png"
        self._graph().write_png(img_path)

    def __init__(self, detection_engine: DetectionEngine, labeling_engine: LabelingEngine):
        super().__init__()
        self.detection_engine = detection_engine
        self.labeling_engine = labeling_engine
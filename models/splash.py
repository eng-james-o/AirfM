# this is supposed to initialise the necessary modules
# check which version of pyside is installed on the system and tailor the imports in main.py accordingly which means that this file should either run before main.py, or main.py should do only what is necessary to run the splash first before calling this file, and then this file handles the rest of the setup
# it is supposed to setup the paths for the airfoils, after checking if they are available
# it should call the script to download the foils and save them, if they do not exist

from PySide2.QtCore import QObject, Slot, Signal, Property, QThread
import logging
import time

from scripts.functions import get_foils_from_dir
from globals import AIRFOILS_FOLDER
from models.data import AirfoilListModel

# set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8', level=logging.INFO)

airfoil_listmodel = AirfoilListModel()

class LoaderThread(QThread):
    loadingProgress = Signal(int, str)
    loadingComplete = Signal()
    step_number = 0

    def run(self):
        # step 1: initialise
        step = "Initialisation"
        self.process_step(1, step)

        # step 2: read airfoils
        airfoils = get_foils_from_dir(AIRFOILS_FOLDER)
        logger.info(f"{len(airfoils)} airfoils")
        for filename, filepath in airfoils:
            airfoil_listmodel.addItem(filename, filepath)
            step = f"Load {filename} airfoil"
            self.process_step(1, step)

        # step 3: load main qml
        step = "Load main QML"
        self.process_step(1, step)
        time.sleep(0.5) # small delay to ensure that the progressbar reaches the end before the splash screen closes
        self.completed = True

        self.loadingComplete.emit()
    
    def process_step(self, level:int, step:str):
        self.step_number += 1
        time.sleep(0.01) # small delay to ensure that the UI has time to update before the next value is sent
        logger.log(level=level, msg=step)
        self.loadingProgress.emit(self.step_number, step)

class SplashController(QObject):
    completed = False
    loadingProgress = Signal(int, str)
    loadingComplete = Signal()

    def __init__(self, parent=None):
        super(SplashController, self).__init__(parent)
        self.thread = LoaderThread()
        self.thread.loadingProgress.connect(self.update_progress)
        self.thread.loadingComplete.connect(self.finish_loading)

    @Slot()
    def initialise_app(self):
        self.thread.start()
    
    @Slot()
    def update_progress(self, step_number, step):
        self.loadingProgress.emit(step_number, step)
    
    def finish_loading(self):
        self.loadingComplete.emit()
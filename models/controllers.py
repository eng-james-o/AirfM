# this is supposed to initialise the necessary modules
# check which version of pyside is installed on the system and tailor the imports in main.py accordingly which means that this file should either run before main.py, or main.py should do only what is necessary to run the splash first before calling this file, and then this file handles the rest of the setup
# it is supposed to setup the paths for the airfoils, after checking if they are available
# it should call the script to download the foils and save them, if they do not exist

from PySide2.QtCore import QObject, Slot, Signal, Property, QThread
import logging
import time

from scripts.functions import get_foils_from_dir
from globals import AIRFOILS_FOLDER
from models.data import AirfoilListModel, ProjectListModel
import os
from PySide2.QtWidgets import QFileDialog

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

class ProjectController(QObject):
    def __init__(self, parent=None):
        super(ProjectController, self).__init__(parent)
    
    @Slot()
    def new_project(self):
        """
        Creates a new project stored as a file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        """
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Create New Project",
            "",
            "Airfoil Project Files (*.afm);;All Files (*)",
            options=options
        )

        if file_path:
            # Ensure the file has the correct extension
            if not file_path.endswith(".afm"):
                file_path += ".afm"

            # Create an empty project file
            try:
                with open(file_path, 'w') as project_file:
                    project_file.write("# Airfoil Project File\n")
                    project_file.write("# This file stores airfoils, transformations, and derived airfoils\n")
                logger.info(f"New project created at {file_path}")
            except Exception as e:
                logger.error(f"Failed to create project file: {e}")

    @Slot(str)
    def open_project(self):
        """
        Opens an existing project file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open Project",
            "",
            "Airfoil Project Files (*.afm);;All Files (*)",
            options=options
        )

        if file_path:
            # Load the project file
            try:
                with open(file_path, 'r') as project_file:
                    content = project_file.read()
                logger.info(f"Project opened from {file_path}")
            except Exception as e:
                logger.error(f"Failed to open project file: {e}")

class MainController(QObject):
    def __init__(self, parent = ...):
        super(MainController, self).__init__(parent)
    
    def save(self):
        """
        Save the project progress into the .afm file
        """
        # Implement the save logic here
        pass
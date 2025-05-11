# this is supposed to initialise the necessary modules
# check which version of pyside is installed on the system and tailor the imports in main.py accordingly which means that this file should either run before main.py, or main.py should do only what is necessary to run the splash first before calling this file, and then this file handles the rest of the setup
# it is supposed to setup the paths for the airfoils, after checking if they are available
# it should call the script to download the foils and save them, if they do not exist
import json
from PySide2.QtCore import QObject, Slot, Signal, Property, QThread
import logging
import time

from scripts.functions import get_foils_from_dir
from models.airfoils import Airfoil_new, AirfoilTransformation
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
    """
    This class handles the project data, including loading and saving projects, and managing airfoils and transformations."""
    current_project_path = None
    current_project_data = None
    projectSelected = Signal()  # Signal emitted when a project is selected or created

    def __init__(self, parent=None):
        super(ProjectController, self).__init__(parent)
        self.current_project_data = {
            "airfoils": [],
            "transformations": [],
            "derived_airfoils": []
        }
    
    def get_project_data(self):
        """
        Returns the current project data.
        """
        return self.current_project_data

    @Slot(str)
    def new_project(self, project_name):
        """
        Creates a new project stored as a file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        """
        try:
            # Define the default project location
            documents_folder = os.path.expanduser("~\\Documents")
            airfm_folder = os.path.join(documents_folder, "Airfm")
            os.makedirs(airfm_folder, exist_ok=True)

            # Create the project directory
            project_path = os.path.join(airfm_folder, project_name)
            os.makedirs(project_path, exist_ok=True)

            # Create the exports folder inside the project directory
            exports_path = os.path.join(project_path, "exports")
            os.makedirs(exports_path, exist_ok=True)

            # Create the .afm project file
            project_file_path = os.path.join(project_path, f"{project_name}.afm")
            self.current_project_path = project_file_path
            self.current_project_data = {
                "airfoils": [],
                "transformations": [],
                "derived_airfoils": []
            }
            self.save_project(project_file_path)
            self.projectSelected.emit()
            logger.info(f"New project created at {project_file_path}")
        except Exception as e:
            logger.error(f"Failed to create new project: {e}")

    @Slot(str)
    def open_project(self, project_file_path):
        """
        Opens an existing project file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        """
        try:
            with open(project_file_path, 'r') as project_file:
                self.current_project_data = json.load(project_file)
            self.current_project_path = project_file_path
            self.projectSelected.emit()
            logger.info(f"Project opened from {project_file_path}")
        except Exception as e:
            logger.error(f"Failed to open project file: {e}")

    @Slot()
    def save_current_project(self):
        """
        Saves the current project to its file.
        """
        if self.current_project_path:
            self.save_project(self.current_project_path)
        else:
            logger.warning("No project path specified. Cannot save project.")

    def save_project(self, file_path):
        """
        Saves the project data to the specified file.
        """
        try:
            with open(file_path, 'w') as project_file:
                json.dump(self.current_project_data, project_file, indent=4)
            logger.info(f"Project saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save project file: {e}")
            return False
    
    def select_project(self, project_path):
        """
        Selects a project and emits the projectSelected signal.
        """
        self.current_project_path = project_path
        self.projectSelected.emit()
        logger.info(f"Project selected: {project_path}")

    @Slot(str, str)
    def add_airfoil(self, name, path):
        if self.current_project_data:
            self.current_project_data["airfoils"].append({"name": name, "path": path})
            logger.info(f"Airfoil {name} added to the project")
        else:
            logger.warning("Cannot add airfoil. No project opened.")

    @Slot(str, str, object)
    def add_transformation(self, airfoil_name, transformation_type, parameters):
        if self.current_project_data:
            transformation = {
                "airfoil_name": airfoil_name,
                "type": transformation_type,
                "parameters": parameters.toVariant()  # Convert QVariant to Python object
            }
            self.current_project_data["transformations"].append(transformation)
            logger.info(f"Transformation {transformation_type} added to {airfoil_name}")
        else:
            logger.warning("Cannot add transformation. No project opened.")

class MainController(QObject):
    """
    This class handles the main application logic, including saving and closing projects.
    """

    def __init__(self, project_controller, parent = None):
        super(MainController, self).__init__(parent)
        self.project_controller = project_controller

    @Slot()
    def save_project(self):
        self.project_controller.save_current_project()
    @Slot()
    def close_project(self):
        self.project_controller.current_project_path = None
        self.project_controller.current_project_data = None
# this is supposed to initialise the necessary modules
# check which version of pyside is installed on the system and tailor the imports in main.py accordingly which means that this file should either run before main.py, or main.py should do only what is necessary to run the splash first before calling this file, and then this file handles the rest of the setup
# it is supposed to setup the paths for the airfoils, after checking if they are available
# it should call the script to download the foils and save them, if they do not exist
import json
from PySide2.QtCore import QObject, Slot, Signal, Property, QThread
from datetime import datetime
import time

from scripts.functions import get_foils_from_dir
from models.airfoils import Airfoil_new, AirfoilTransformation
from globals import AIRFOILS_FOLDER
from models.data import AirfoilListModel, RecentProjectsModel, AirfoilActionModel
import os
from PySide2.QtWidgets import QFileDialog

# set up logger
from logger_config import logger

airfoil_listmodel = AirfoilListModel()

class LoaderThread(QThread):
    loadingProgress = Signal(int, str)
    loadingComplete = Signal()
    step_number = 0
    steps = list()

    def run(self):
        # step 1: initialise
        self.steps.append("Initialisation")
        self.process_step(1, self.steps[-1])

        # step 2: read airfoils
        airfoils = get_foils_from_dir(AIRFOILS_FOLDER)
        logger.info(f"{len(airfoils)} airfoils")
        self.steps.append(f"Load airfoils")
        self.process_step(1, self.steps[-1])
        for filename, filepath in airfoils:
            airfoil_listmodel.addItem(filename, filepath)

        # step 3: load main qml
        self.steps.append("Load main QML")
        self.process_step(1, self.steps[-1])
        time.sleep(0.5) # small delay to ensure that the progressbar reaches the end before the splash screen closes
        self.completed = True

        self.loadingComplete.emit()
    
    def process_step(self, level:int, step:str):
        self.step_number += 1

        # small delay to ensure that the UI has time to update visibly before the next value is sent
        time.sleep(0.1) 
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
    This class handles the project data, including loading and saving a project, and managing airfoils and transformations within the project.
    """
    current_project_path = None
    current_project_data = None
    projectSelected = Signal()  # Signal emitted when a project is selected or created

    def __init__(self, parent=None, recent_projects_model=None):
        """
        Args:
            parent (QObject): Parent object for this controller.
            recent_projects_model (RecentProjectsModel): Model for recent projects.
        """
        super(ProjectController, self).__init__(parent)
        self.current_project_data = {
            "airfoils": [],
            "transformations": [],
            "derived_airfoils": []
        }
        self.airfoil_action_model = AirfoilActionModel()
    
    def get_project_data(self):
        """
        Returns the current project data.
        """
        return self.current_project_data

    def add_to_recent_projects(self, name, path, date=None):
        """
        Adds the accessed project to the RecentProjectsModel's database.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Use a singleton or global instance if available, else create a temp one
        try:
            if hasattr(self, 'recent_projects_model'):
                model = self.recent_projects_model
            else:
                model = RecentProjectsModel()
                self.recent_projects_model = model
            model.addItem(name, path, date)
        except Exception as e:
            logger.error(f"Failed to add project to recent projects: {e}")

    @Slot(str, str)
    def new_project(self, project_name, folder_url):
        """
        Creates a new project stored as a file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        Args:
            project_name (str): The name of the project.
            folder_url (str): The folder URL where the project should be created.
        """
        print(f"Create new project called: Name: {project_name} Location: {folder_url}")
        try:
            # Convert QML file dialog URL (e.g., "file:///C:/Users/...") to a local path
            if folder_url.startswith("file:///"):
                folder_path = folder_url[8:] if os.name == "nt" else folder_url[7:]
            else:
                folder_path = folder_url

            # # Define the default project location
            # documents_folder = os.path.expanduser("~\\Documents")
            # airfm_folder = os.path.join(documents_folder, "Airfm")
            # os.makedirs(airfm_folder, exist_ok=True)

            # Create the project directory
            project_path = os.path.join(folder_path, project_name)
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
            # Add to recent projects
            self.add_to_recent_projects(project_name, project_file_path)
            self.projectSelected.emit()
            logger.info(f"New project created at {project_file_path}")

        except Exception as e:
            logger.error(f"Failed to create new project: {e}")

    @Slot(str)
    def open_project(self, project_file_path):
        """
        Opens an existing project file with .afm extension. This file stores the airfoils, the list of transformations done on them, and the list of airfoils that are derived from them.
        """
        if project_file_path.startswith("file:///"):
            # Convert QML file dialog URL (e.g., "file:///C:/Users/...") to a local path
            project_file_path = project_file_path[8:] if os.name == "nt" else project_file_path[7:]
        try:
            with open(project_file_path, 'r') as project_file:
                self.current_project_data = json.load(project_file)
            self.current_project_path = project_file_path

            # Add to recent projects
            project_name = os.path.splitext(os.path.basename(project_file_path))[0]
            self.add_to_recent_projects(project_name, project_file_path)
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
            print(f"Failed to save project file: {e}")
            logger.error(f"Failed to save project file: {e}")
            return False
    
    def select_project(self, project_path):
        """
        Selects a project and emits the projectSelected signal.
        """
        self.current_project_path = project_path
        self.projectSelected.emit()
        logger.info(f"Project selected: {project_path}")

    @Slot(int, str)
    def add_airfoil(self, airfoil_id, name):
        """Add an airfoil to the project and AirfoilActionModel."""
        if self.current_project_data:
            self.current_project_data["airfoils"].append({"id": airfoil_id, "name": name})
            self.airfoil_action_model.addAirfoil(airfoil_id, name, [])
            logger.info(f"Airfoil {name} (id={airfoil_id}) added to the project")
        else:
            logger.warning("Cannot add airfoil. No project opened.")

    @Slot(int, str, object)
    def add_transformation(self, airfoil_id, transformation_type, parameters):
        """Add a transformation to a specific airfoil in AirfoilActionModel and project data."""
        if self.current_project_data:
            # Add to AirfoilActionModel
            self.airfoil_action_model.addTransformation(airfoil_id, transformation_type, parameters)
            # Add to project data (for persistence)
            self.current_project_data["transformations"].append({
                "airfoil_id": airfoil_id,
                "type": transformation_type,
                "parameters": parameters
            })
            logger.info(f"Transformation {transformation_type} added to airfoil id={airfoil_id}")
        else:
            logger.warning("Cannot add transformation. No project opened.")

    @Slot(int)
    def remove_airfoil(self, airfoil_id):
        """Remove an airfoil and its transformations from the project and AirfoilActionModel."""
        # Remove from AirfoilActionModel
        self.airfoil_action_model.removeAirfoil(airfoil_id)
        # Remove from project data
        self.current_project_data["airfoils"] = [a for a in self.current_project_data["airfoils"] if a["id"] != airfoil_id]
        self.current_project_data["transformations"] = [t for t in self.current_project_data["transformations"] if t.get("airfoil_id") != airfoil_id]
        logger.info(f"Airfoil id={airfoil_id} removed from project")

    @Slot(int)
    def clear_transformations(self, airfoil_id):
        """Clear all transformations for a specific airfoil in AirfoilActionModel and project data."""
        self.airfoil_action_model.clearTransformations(airfoil_id)
        self.current_project_data["transformations"] = [t for t in self.current_project_data["transformations"] if t.get("airfoil_id") != airfoil_id]
        logger.info(f"Transformations cleared for airfoil id={airfoil_id}")

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
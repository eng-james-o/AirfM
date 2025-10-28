# this is supposed to initialise the necessary modules
# check which version of pyside is installed on the system and tailor the imports in main.py accordingly which means that this file should either run before main.py, or main.py should do only what is necessary to run the splash first before calling this file, and then this file handles the rest of the setup
# it is supposed to setup the paths for the airfoils, after checking if they are available
# it should call the script to download the foils and save them, if they do not exist
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from PySide2.QtCore import QObject, Slot, Signal, QThread
from PySide2.QtWidgets import QFileDialog

from scripts.functions import get_foils_from_dir, get_save_airfoils
from models.airfoils import Airfoil_new, AirfoilTransformation
from globals import AIRFOILS_FOLDER
from models.data import AirfoilListModel, RecentProjectsModel, AirfoilActionModel

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
        airfoil_listmodel.clear()
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
        self.recent_projects_model = recent_projects_model
        self.current_project_data = {
            "airfoils": [],
            "transformations": [],
            "derived_airfoils": []
        }
        self.airfoil_action_model = AirfoilActionModel()
        self.loaded_airfoils: Dict[int, Airfoil_new] = {}
    
    def get_project_data(self):
        """
        Returns the current project data.
        """
        return self.current_project_data

    @staticmethod
    def _normalise_file_reference(path: str) -> str:
        """Convert a QML ``file:///`` URL into a filesystem path."""

        if path.startswith("file:///"):
            return path[8:] if os.name == "nt" else path[7:]
        return path

    @staticmethod
    def _normalise_parameters(parameters: Any) -> Dict[str, Any]:
        """Convert QVariant-style parameter objects into plain dictionaries."""

        if isinstance(parameters, dict):
            mapping = parameters
        elif hasattr(parameters, "toVariantMap"):
            mapping = dict(parameters.toVariantMap())  # type: ignore[attr-defined]
        elif hasattr(parameters, "toVariant"):
            value = parameters.toVariant()
            mapping = dict(value) if isinstance(value, dict) else {"value": value}
        else:
            mapping = {"value": parameters}

        normalised: Dict[str, Any] = {}
        for key, value in mapping.items():
            if isinstance(value, (int, float)):
                normalised[key] = float(value)
                continue
            try:
                normalised[key] = float(value)
            except (TypeError, ValueError):
                normalised[key] = value
        return normalised

    def _load_airfoil_instance(self, airfoil_id: int, name: str, path: Optional[str]) -> Optional[Airfoil_new]:
        """Ensure an :class:`Airfoil_new` instance is cached for ``airfoil_id``."""

        if airfoil_id in self.loaded_airfoils:
            return self.loaded_airfoils[airfoil_id]

        if not path:
            logger.warning("No path supplied for airfoil %s", name)
            return None

        try:
            foil = Airfoil_new()
            foil.load(path)
        except Exception as exc:
            logger.error("Failed to load airfoil %s from %s: %s", name, path, exc)
            return None

        self.loaded_airfoils[airfoil_id] = foil
        return foil

    def _serialise_surface(self, x: np.ndarray, y: np.ndarray) -> List[List[float]]:
        return [[float(xx), float(yy)] for xx, yy in zip(x.tolist(), y.tolist())]

    def _record_transformation(
        self,
        airfoil_id: int,
        transformation_type: str,
        parameters: Dict[str, Any],
        upper_x: np.ndarray,
        upper_y: np.ndarray,
        lower_x: np.ndarray,
        lower_y: np.ndarray,
    ) -> Dict[str, Any]:
        return {
            "airfoil_id": airfoil_id,
            "type": transformation_type,
            "parameters": parameters,
            "upper_surface": self._serialise_surface(upper_x, upper_y),
            "lower_surface": self._serialise_surface(lower_x, lower_y),
        }

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
            folder_path = self._normalise_file_reference(folder_url)

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
            self.loaded_airfoils.clear()
            self.airfoil_action_model.clear()
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
        project_file_path = self._normalise_file_reference(project_file_path)
        try:
            with open(project_file_path, 'r') as project_file:
                data = json.load(project_file)
            self.current_project_data = {
                "airfoils": data.get("airfoils", []),
                "transformations": data.get("transformations", []),
                "derived_airfoils": data.get("derived_airfoils", []),
            }
            self.current_project_path = project_file_path

            self.airfoil_action_model.clear()
            self.loaded_airfoils.clear()

            for airfoil in self.current_project_data["airfoils"]:
                airfoil_id = airfoil.get("id")
                name = airfoil.get("name", "")
                path = airfoil.get("path")
                self.airfoil_action_model.addAirfoil(airfoil_id, name, [])
                if path:
                    self._load_airfoil_instance(airfoil_id, name, self._normalise_file_reference(path))

            for transformation in self.current_project_data["transformations"]:
                airfoil_id = transformation.get("airfoil_id")
                transformation_type = transformation.get("type", "")
                params = transformation.get("parameters", {})
                self.airfoil_action_model.addTransformation(airfoil_id, transformation_type, params)

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

    def _find_airfoil_path(self, name: str) -> Optional[str]:
        for row in range(airfoil_listmodel.rowCount()):
            index = airfoil_listmodel.index(row, 0)
            if airfoil_listmodel.data(index, AirfoilListModel.NameRole) == name:
                return airfoil_listmodel.data(index, AirfoilListModel.PathRole)
        return None

    @Slot(int, str)
    @Slot(int, str, str)
    def add_airfoil(self, airfoil_id, name, path=""):
        """Add an airfoil to the project and AirfoilActionModel."""

        if not self.current_project_data:
            logger.warning("Cannot add airfoil. No project opened.")
            return

        for existing in self.current_project_data["airfoils"]:
            if existing.get("id") == airfoil_id:
                logger.info("Airfoil id=%s already exists in project", airfoil_id)
                return

        resolved_path = self._normalise_file_reference(path) if path else self._find_airfoil_path(name)
        airfoil_entry = {"id": airfoil_id, "name": name}
        if resolved_path:
            airfoil_entry["path"] = resolved_path

        self.current_project_data["airfoils"].append(airfoil_entry)
        self.airfoil_action_model.addAirfoil(airfoil_id, name, [])
        self._load_airfoil_instance(airfoil_id, name, resolved_path)
        logger.info(f"Airfoil {name} (id={airfoil_id}) added to the project")

    @Slot(int, str, object)
    def add_transformation(self, airfoil_id, transformation_type, parameters):
        """Add a transformation to a specific airfoil in AirfoilActionModel and project data."""

        if not self.current_project_data:
            logger.warning("Cannot add transformation. No project opened.")
            return

        normalised_parameters = self._normalise_parameters(parameters)
        airfoil = self.loaded_airfoils.get(airfoil_id)

        if not airfoil:
            logger.warning("Airfoil id=%s not loaded; attempting reload", airfoil_id)
            airfoil_info = next((item for item in self.current_project_data["airfoils"] if item.get("id") == airfoil_id), None)
            if airfoil_info:
                airfoil = self._load_airfoil_instance(
                    airfoil_id,
                    airfoil_info.get("name", ""),
                    airfoil_info.get("path"),
                )

        if not airfoil:
            logger.warning("Cannot add transformation. Airfoil id=%s unavailable", airfoil_id)
            return

        upper_x = np.array(airfoil.UPPER_X, copy=True)
        upper_y = np.array(airfoil.UPPER_Y, copy=True)
        lower_x = np.array(airfoil.LOWER_X, copy=True)
        lower_y = np.array(airfoil.LOWER_Y, copy=True)

        transform_method = {
            "scale": lambda: AirfoilTransformation.scale_to(
                upper_x.copy(), upper_y.copy(), lower_x.copy(), lower_y.copy(),
                normalised_parameters.get("chord") or normalised_parameters.get("scale", 1.0)
            ),
            "translate": lambda: AirfoilTransformation.translate_to(
                upper_x.copy(),
                upper_y.copy(),
                lower_x.copy(),
                lower_y.copy(),
                normalised_parameters.get("x", 0.0),
                normalised_parameters.get("y", 0.0),
            ),
            "rotate": lambda: AirfoilTransformation.rotate_to(
                upper_x.copy(),
                upper_y.copy(),
                lower_x.copy(),
                lower_y.copy(),
                normalised_parameters.get("angle", 0.0),
            ),
        }.get(transformation_type.lower())

        if transform_method is None:
            logger.warning("Unknown transformation type %s", transformation_type)
            return

        try:
            transformed = transform_method()
        except Exception as exc:
            logger.error("Failed to apply transformation %s: %s", transformation_type, exc)
            return

        if transformed is None:
            logger.warning("Transformation %s produced no result", transformation_type)
            return

        transformed_upper_x, transformed_upper_y, transformed_lower_x, transformed_lower_y = transformed

        self.airfoil_action_model.addTransformation(airfoil_id, transformation_type, normalised_parameters)
        self.current_project_data["transformations"].append({
            "airfoil_id": airfoil_id,
            "type": transformation_type,
            "parameters": normalised_parameters,
        })
        self.current_project_data["derived_airfoils"].append(
            self._record_transformation(
                airfoil_id,
                transformation_type,
                normalised_parameters,
                transformed_upper_x,
                transformed_upper_y,
                transformed_lower_x,
                transformed_lower_y,
            )
        )
        logger.info(f"Transformation {transformation_type} added to airfoil id={airfoil_id}")

    @Slot(int)
    def remove_airfoil(self, airfoil_id):
        """Remove an airfoil and its transformations from the project and AirfoilActionModel."""
        # Remove from AirfoilActionModel
        self.airfoil_action_model.removeAirfoil(airfoil_id)
        # Remove from project data
        self.current_project_data["airfoils"] = [a for a in self.current_project_data["airfoils"] if a["id"] != airfoil_id]
        self.current_project_data["transformations"] = [
            t for t in self.current_project_data["transformations"] if t.get("airfoil_id") != airfoil_id
        ]
        self.current_project_data["derived_airfoils"] = [
            d for d in self.current_project_data["derived_airfoils"] if d.get("airfoil_id") != airfoil_id
        ]
        self.loaded_airfoils.pop(airfoil_id, None)
        logger.info(f"Airfoil id={airfoil_id} removed from project")

    @Slot(int)
    def clear_transformations(self, airfoil_id):
        """Clear all transformations for a specific airfoil in AirfoilActionModel and project data."""
        self.airfoil_action_model.clearTransformations(airfoil_id)
        self.current_project_data["transformations"] = [
            t for t in self.current_project_data["transformations"] if t.get("airfoil_id") != airfoil_id
        ]
        self.current_project_data["derived_airfoils"] = [
            d for d in self.current_project_data["derived_airfoils"] if d.get("airfoil_id") != airfoil_id
        ]
        logger.info(f"Transformations cleared for airfoil id={airfoil_id}")

    @Slot(result='QVariantMap')
    @Slot(str, result='QVariantMap')
    @Slot(str, bool, result='QVariantMap')
    @Slot(str, bool, int, result='QVariantMap')
    def refresh_airfoil_library(self, target_dir="", overwrite=False, limit=-1):
        """Download the latest airfoil library and refresh the list model."""

        directory = self._normalise_file_reference(target_dir) if target_dir else AIRFOILS_FOLDER
        limit_value = None if limit is None or limit < 0 else limit

        result = get_save_airfoils(directory, overwrite=overwrite, limit=limit_value)
        airfoil_listmodel.loadFromDirectory(directory)

        summary = {
            "saved": len(result.saved),
            "skipped": len(result.skipped),
            "errors": [str(error) for _, error in result.errors],
            "directory": directory,
        }
        if result.errors:
            logger.warning("Airfoil library refresh completed with errors: %s", summary["errors"])
        else:
            logger.info(
                "Airfoil library refreshed: %s saved, %s skipped", summary["saved"], summary["skipped"]
            )
        return summary

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
        self.project_controller.airfoil_action_model.clear()
        self.project_controller.loaded_airfoils.clear()
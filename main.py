import os, sys
from pathlib import Path

from PySide2.QtCore import QUrl, QCoreApplication

QCoreApplication.setOrganizationName("Aerohub")
QCoreApplication.setApplicationName("Airfoil Design Tool")
QCoreApplication.setApplicationVersion("0.1.0")

from PySide2.QtGui import QGuiApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCharts import QtCharts
from PySide2.QtWidgets import QApplication, QMainWindow 

from models.data import AirfoilListModel, RecentProjectsModel
from models.airfoils import Airfoil_new
from models.controllers import SplashController, ProjectController, MainController, airfoil_listmodel
from scripts.functions import get_foils_from_dir

import globals
from logger_config import logger

# TODO:
# - Add the database setup to the splash screen
# - Make the splash screen do some more useful functions, such as creating the necessary databases, components, etc.
# - Add the ability to select a project from the recent projects list
# - Setup the database for the recent projects list

# FIXME:
# - Fix the StandardPaths in the qml
# - Fix the loading of the main qml file, screens are being muddled up
# - Fix the connections to the dataModel and airfoilListModel
# - The appbar button tips and hover effects only work on the upper part of the buttons


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    root_context = engine.rootContext()

    splash_controller = SplashController()
    data_model = Airfoil_new()
    recent_projects_model = RecentProjectsModel()
    project_controller = ProjectController(recent_projects_model=recent_projects_model)
    main_controller = MainController(project_controller=project_controller)

    # Function to load the project page
    def load_project_page():
        logger.info("Splash screen Loading complete")
        engine.clearComponentCache()
        root_context.setContextProperty("projectController", project_controller)
        try:
            engine.load(QUrl.fromLocalFile(os.path.join(globals.APP_SHELL_QML_FILE)))
            splash_screen = engine.rootObjects()[0]
            splash_screen.deleteLater()
        except Exception as e:
            logger.critical(f"Failed to load project page: {e}")
    
    # Function to load the main application page
    def load_main_page():
        logger.info("Project page complete")
        engine.clearComponentCache()
        root_context.setContextProperty("projectController", project_controller)
        root_context.setContextProperty("dataModel", data_model)
        root_context.setContextProperty("airfoilListModel", airfoil_listmodel)
        root_context.setContextProperty("airfoilActionModel", project_controller.airfoil_action_model)

    # Connect signals for transitions
    splash_controller.loadingComplete.connect(load_project_page)
    project_controller.projectSelected.connect(load_main_page)

    # Load the splash screen
    root_context.setContextProperty("splashController", splash_controller)
    root_context.setContextProperty("recentProjectsModel", recent_projects_model)
    engine.load(globals.SPLASH_QML_FILE) # SPLASH_QML_FILE or APP_SHELL_QML_FILE
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec_())

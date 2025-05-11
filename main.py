import os, sys
from pathlib import Path

from PySide2.QtCore import Property, QObject, QUrl, Qt, QFile, Signal, Slot
from PySide2.QtGui import QGuiApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCharts import QtCharts
from PySide2.QtWidgets import QApplication, QMainWindow 

from models.data import AirfoilListModel
from models.airfoils import Airfoil_new
from scripts.functions import get_foils_from_dir
import globals
from models.controllers import SplashController, ProjectController, MainController, airfoil_listmodel

from logger_config import logger
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    root_context = engine.rootContext()

    splash_controller = SplashController()
    project_controller = ProjectController()
    main_controller = MainController(project_controller=project_controller)
    data_model = Airfoil_new()

    # Function to load the project page
    def load_project_page():
        logger.info("Splash screen Loading complete")
        engine.clearComponentCache()
        root_context.setContextProperty("projectController", project_controller)
        try:
            engine.load(QUrl.fromLocalFile(os.path.join(globals.MAIN_QML_FILE)))
            splash_screen = engine.rootObjects()[0]
            splash_screen.deleteLater()
            
            # main_window = engine.rootObjects()[0]
            # main_window.setProperty("currentPage", "SelectFoilPage_new.qml")
        except Exception as e:
            logger.critical(f"Failed to load project page: {e}")
    
    # Function to load the main application page
    def load_main_page():
        logger.info("Project page complete")
        engine.clearComponentCache()
        root_context.setContextProperty("dataModel", data_model)
        root_context.setContextProperty("airfoilListModel", airfoil_listmodel)
        # root_context.setContextProperty("projectController", project_controller)
        # try:
        #     engine.load(globals.MAIN_QML_FILE)
        # except Exception as e:
        #     logger.critical(f"Failed to load main application page: {e}")

    # Connect signals for transitions
    splash_controller.loadingComplete.connect(load_project_page)
    project_controller.projectSelected.connect(load_main_page)

    # Load the splash screen
    root_context.setContextProperty("splashController", splash_controller)
    engine.load(globals.SPLASH_QML_FILE) # SPLASH_QML_FILE or MAIN_QML_FILE
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec_())
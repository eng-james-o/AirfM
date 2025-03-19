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
from models.splash import SplashController, airfoil_listmodel

from logger_config import logger
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    root_context = engine.rootContext()

    splash_controller = SplashController()
    data_model = Airfoil_new()

    root_context.setContextProperty("splashController", splash_controller)

    engine.load(globals.SPLASH_QML_FILE) # SPLASH_QML_FILE or MAIN_QML_FILE
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    def load_main():
        # Load main screen
        engine.clearComponentCache()
        root_context.setContextProperty("dataModel", data_model)
        root_context.setContextProperty("airfoilListModel", airfoil_listmodel)
        try:
            engine.load(globals.MAIN_QML_FILE)
            splash_screen = engine.rootObjects()[0]
            splash_screen.deleteLater()
        except Exception as e:
            logger.critical(e)
        
    splash_controller.loadingComplete.connect(load_main)
    sys.exit(app.exec_())
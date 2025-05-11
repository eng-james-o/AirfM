import os
from pathlib import Path

# Absolute path to the top-level directory of the project
PROJECT_DIR = Path(__file__).resolve().parent

# Relative path to the airfoils folder
# AIRFOILS_FOLDER = os.fspath(PROJECT_DIR / 'airfoils')
AIRFOILS_FOLDER = os.path.join(PROJECT_DIR / 'airfoils' / 'airfoil_archive')

# Relative path to the qml files
MAIN_QML_FILE = os.path.join(PROJECT_DIR, 'qml', 'main.qml')
SPLASH_QML_FILE = os.path.join(PROJECT_DIR, 'qml', 'splash.qml')
PROJECT_PAGE_QML_FILE = os.path.join(PROJECT_DIR, 'qml/pages/SelectProjectPage.qml')
MAIN_PAGE_QML_FILE = os.path.join(PROJECT_DIR, 'qml/pages/SelectFoilPage_new.qml')
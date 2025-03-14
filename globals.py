import os
from pathlib import Path

# Absolute path to the top-level directory of the project
PROJECT_DIR = Path(__file__).resolve().parent

# Relative path to the airfoils folder
AIRFOILS_FOLDER = os.fspath(PROJECT_DIR / 'airfoils')

# Relative path to the main.qml file
MAIN_QML_FILE = os.path.join(PROJECT_DIR / 'qml', 'main.qml')
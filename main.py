# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
#import numpy as np

from PySide2.QtCore import QObject #, QUrl, Qt, QFile
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
#from PySide2.QtCharts import QtCharts

class AirfoilModel(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = [] # supposed to contain tuples of (x,y)
    
    def load(self, airfoil_path):
        '''Load the data from the dat file into the object and returns 2 matrices upper and lower, which contain 2 vectors each: X and Y'''

        # claim and initialize variables
        self.NUM_POINTS = None

        try:
            with open(airfoil_path) as airfoil_dat:
                contents = airfoil_dat.readlines()
        except Exception as e:
            print(f"Error -> {e}")
        else:
            for line in contents:
                # strip whitespaces and split the line by spaces
                line_content = line.strip().split()
                if len(line_content) < 1:
                    # continue to next line if the line is Empty
                    continue
                
                # non-empty line starting with alphabet
                elif line_content[0].isalpha():
                    if self.NAME:
                        # if name has been defined already and another alphabet line is encountered, show warning and skip
                        print(f"Warning on line{contents.index(line)}, expected numeric, instead found:\n{' '.join(line_content)}")
                        continue
                    # If line contains alphabets, its the name line
                    self.NAME = ' '.join(line_content)

                elif float(line_content[0]) > 1:
                    # Number of data points
                    if self.NUM_POINTS:
                        # if num_points has been defined already and another line with large value is encountered,
                        # show warning and skip
                        print(f"Warning on line{contents.index(line)}, expected airfoil data, instead found:\n{' '.join(line_content)}")
                        continue
                    # num_points = list(map(int, list(map(float, line_content))))
                    num_points_upper = int(float(line_content[0]))
                    num_points_lower = int(float(line_content[1]))

                elif float(line_content[0]) <= 1:
                    # append Individual data point as a tuple of x and y values to raw
                    self._data.append(tuple(map(float, line_content)))

    def data(self):
        return self._data
    
if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    data_model = AirfoilModel()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("dataModel", data_model)
    engine.load(os.fspath(Path(__file__).resolve().parent / "qml/main.qml"))
    #engine.load(r"C:\Users\PC\Documents\qt_projects\AirfoilManipulate\qml\main.qml")

    if not engine.rootObjects():
        print(-1)
        sys.exit(-1)
    sys.exit(app.exec_())

"""
This module contains various model classes that are not directly based on airfoil shapes.

Classes:
    DataPoint: A Qt Object that contains the x and y values of a single data point
    Airfoils: A Qt ListModel that contains the names and paths of all the available airfoils in the database
"""
# This Python file uses the following encoding: utf-8

from typing import Dict

import numpy as np
from scipy.interpolate import interp1d
# from scipy.misc import derivative
import matplotlib.pyplot as plt
import logging

import re
import os
from pathlib import Path
import sys

from PySide2.QtCore import Property, QAbstractListModel, QObject, Qt, Signal, Slot

# Qt Model classes
class DataPoint(QObject):
    def __init__(self, data_tuple, parent=None):
        """
        
        """
        super().__init__(parent)
        self._x = data_tuple[0]
        self._y = data_tuple[1]
        
        if len(data_tuple) > 2:
            self._z = data_tuple[2]

    def getX(self):
        return self._x

    def getY(self):
        return self._y
    
    def getZ(self):
        try:
            return self._z
        except:
            return None

    x = Property(float, getX)
    y = Property(float, getY)
    z = Property(float, getZ)
       
class AirfoilListModel(QAbstractListModel):
    """This model contains the available airfoils, name and path"""
    PathRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paths = list()
        self._names = list()
    
    def rowCount(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == AirfoilListModel.PathRole:
            return self._paths[index.row()]
        elif role == AirfoilListModel.NameRole:
            return self._names[index.row()]
        return None
    
    def roleNames(self) -> Dict:
        roles = {AirfoilListModel.PathRole: b"path", AirfoilListModel.NameRole: b"name"}
        return roles

"""
This module contains various model classes that are not directly based on airfoil shapes.

Classes:
    Airfoils: A Qt ListModel that contains the names and paths of all the available airfoils in the database
"""
# This Python file uses the following encoding: utf-8

from typing import Dict

import numpy as np
from scipy.interpolate import interp1d
# from scipy.misc import derivative
import matplotlib.pyplot as plt
from logger_config import logger

from pathlib import Path
import sys

from PySide2.QtCore import Property, QAbstractListModel, QObject, Qt, QModelIndex, Signal, Slot
from PySide2.QtGui import QStandardItem, QStandardItemModel

# Qt Model classes

class AirfoilListModel(QAbstractListModel):
    """This List model contains the available airfoils, name and path"""
    PathRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = list()
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        
        item = self._data[index.row()]

        if role == AirfoilListModel.PathRole:
            return item.path
        elif role == AirfoilListModel.NameRole or role == Qt.DisplayRole:
            return item.name
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def roleNames(self) -> Dict:
        roles = {
            AirfoilListModel.PathRole: b"path",
            AirfoilListModel.NameRole: b"name"
            }
        return roles
    
    @Slot(str, str)
    def addItem(self, name, path):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(ModelItem(name, path))
        self.endInsertRows()

class ModelItem:
    """This class represents a single entry of airfoil name and path"""
    def __init__(self, name, path):
        self.name = name
        self.path = path

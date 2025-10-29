"""
This module contains various model classes that are not directly based on airfoil shapes.

Classes:
    AirfoilListModel: A Qt ListModel that contains the names and paths of all the available airfoils in the database
    AirfoilModelItem: 
    ProjectListModel: A Qt ListModel that contains the names
    ProjectModelItem: 

Functions:
    createModelItem: A class factory
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
from models.database import ProjectDatabase
from scripts.functions import get_foils_from_dir

# Qt Model classes

# TODO: Add description (who used the airfoil and where or general properties) and other metadata to the airfoil model (e.g. camber, thickness, etc.) and display it in the airfoil info card
class AirfoilListModel(QAbstractListModel):
    """This List model contains the available airfoils, name and path"""
    PathRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    DescriptionRole = Qt.UserRole + 3
    CamberRole = Qt.UserRole + 4
    ThicknessRole = Qt.UserRole + 5

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
        # elif role == AirfoilListModel.DescriptionRole:
        #     return item.description
        # elif role == AirfoilListModel.CamberRole:
        #     return item.camber
        # elif role == AirfoilListModel.ThicknessRole:
        #     return item.thickness
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
        self._data.append(AirfoilModelItem(name, path))
        self.endInsertRows()

    @Slot()
    def clear(self):
        """Remove all airfoils from the model."""

        if not self._data:
            return
        self.beginResetModel()
        self._data = []
        self.endResetModel()

    @Slot(str)
    def loadFromDirectory(self, directory):
        """Populate the model with airfoils discovered in ``directory``."""

        airfoils = get_foils_from_dir(directory)
        self.beginResetModel()
        self._data = [AirfoilModelItem(name, path) for name, path in airfoils]
        self.endResetModel()

def createModelItem(name, required_attrs):
    """
    This class factory creates a class with the given name and required attributes. It creates classes for the ModelItem for airfoils and for any other list list model needed in this project.
    # Example usage
    AirfoilModelItem = createModelItem("AirfoilModelItem", ["name", "path"])
    
    Args:
        name (str): The name of the class
        required_attrs (list): A list of required attributes
    Returns:
        type: A class with the given name and required attributes
    """
    def __init__(self, *args):
        if len(args) != len(required_attrs):
            raise TypeError(f"{name} requires {len(required_attrs)} arguments: {', '.join(required_attrs)}")
        for attr, value in zip(required_attrs, args):
            setattr(self, attr, value)
    
    return type(name, (object,), {"__init__": __init__})

AirfoilModelItem = createModelItem("AirfoilModelItem", ["name", "path"])
AirfoilModelItem.__doc__ = """
This class represents a single entry of airfoil name and path. 

Args:
    name (str): The name of the airfoil
    path (str): The path to the airfoil
"""
                                   
class RecentProjectsModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    PathRole = Qt.UserRole + 2
    DateRole = Qt.UserRole + 3

    def __init__(self, db_path="projects.db", parent=None):
        super().__init__(parent)
        self.db = ProjectDatabase(db_path)
        # self._data = list()
        self._projects = self._load_from_db()

    def _load_from_db(self):
        """Retrieve recent projects ordered by most recent access without duplicates."""
        projects = self.db.get_projects()
        seen_paths = set()
        unique_projects = []
        for name, path, date in projects:
            if path in seen_paths:
                continue
            unique_projects.append((name, path, date))
            seen_paths.add(path)
        return unique_projects
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._projects)):
            return None
        
        project = self._projects[index.row()]

        if role == RecentProjectsModel.PathRole:
            return project[1] # project.path
        elif role == RecentProjectsModel.NameRole or role == Qt.DisplayRole:
            return project[0] # project.name
        elif role == RecentProjectsModel.DateRole:
            return project[2] # project.date
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._projects)
    
    def roleNames(self) -> Dict:
        roles = {
            RecentProjectsModel.PathRole: b"path",
            RecentProjectsModel.NameRole: b"name",
            RecentProjectsModel.DateRole: b"date"
            }
        return roles
    
    @Slot(str, str)
    def addItem(self, name, path, date):
        # Add the project to the database
        self.db.add_project(name, path, date)
        
        # Refresh so ordering reflects most recent access and duplicates are removed
        self.refresh()
    
    @Slot()
    def refresh(self):
        self.beginResetModel()
        self._projects = self._load_from_db()
        self.endResetModel()

ProjectModelItem = createModelItem("ProjectModelItem", ["name", "path", "date"])
ProjectModelItem.__doc__ = """
This class represents a single entry of project name path and date. 

Args:
    name (str): The name of the project
    path (str): The path to the project
    date (str): The date the project was last modified
"""

class AirfoilActionModel(QAbstractListModel):
    """This List model contains the transformations done on multiple airfoils, each with an id, name, and a list of transformations."""
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    TransformationsRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # Each item: {'id': int, 'name': str, 'transformations': list}

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        item = self._data[index.row()]
        if role == AirfoilActionModel.IdRole:
            return item['id']
        elif role == AirfoilActionModel.NameRole:
            return item['name']
        elif role == AirfoilActionModel.TransformationsRole:
            return item['transformations']
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def roleNames(self) -> Dict:
        return {
            AirfoilActionModel.IdRole: b"id",
            AirfoilActionModel.NameRole: b"name",
            AirfoilActionModel.TransformationsRole: b"transformations"
        }

    @Slot(int, str, list)
    def addAirfoil(self, airfoil_id, name, transformations):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append({'id': airfoil_id, 'name': name, 'transformations': transformations})
        self.endInsertRows()

    @Slot(int, str, object)
    def addTransformation(self, airfoil_id, transformation_type, parameters):
        for item in self._data:
            if item['id'] == airfoil_id:
                item['transformations'].append({'type': transformation_type, 'parameters': parameters})
                self.dataChanged.emit(self.index(self._data.index(item)), self.index(self._data.index(item)))
                break

    @Slot(int)
    def removeAirfoil(self, airfoil_id):
        for i, item in enumerate(self._data):
            if item['id'] == airfoil_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._data.pop(i)
                self.endRemoveRows()
                break

    @Slot(int)
    def clearTransformations(self, airfoil_id):
        for item in self._data:
            if item['id'] == airfoil_id:
                item['transformations'] = []
                self.dataChanged.emit(self.index(self._data.index(item)), self.index(self._data.index(item)))
                break

    @Slot()
    def clear(self):
        """Remove all airfoil entries."""

        if not self._data:
            return
        self.beginResetModel()
        self._data = []
        self.endResetModel()

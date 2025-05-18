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
        self._data.append(AirfoilModelItem(name, path))
        self.endInsertRows()

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
        self._projects = self.db.get_projects()
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        
        project = self._projects[index.row()]

        if role == RecentProjectsModel.PathRole:
            return project[0] # project.path
        elif role == RecentProjectsModel.NameRole or role == Qt.DisplayRole:
            return project[1] # project.name
        elif role == RecentProjectsModel.DateRole:
            return project[2] # project.date
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._projects)
    
    def roleNames(self) -> Dict:
        roles = {
            ProjectListModel.PathRole: b"path",
            ProjectListModel.NameRole: b"name",
            ProjectListModel.DateRole: b"date"
            }
        return roles
    
    @Slot(str, str)
    def addItem(self, name, path, date):
        # Add the project to the database
        self.db.add_project(name, path, date)
        
        # Add the project to the model
        # TODO
        # - change this implementation to simply refresh the model, instead of adding the item to the model
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._projects.append((name, path, date))
        self.endInsertRows()
    
    @Slot()
    def refresh(self):
        self.beginResetModel()
        self._projects = self.db.get_projects()
        self.endResetModel()

ProjectModelItem = createModelItem("ProjectModelItem", ["name", "path", "date"])
ProjectModelItem.__doc__ = """
This class represents a single entry of project name path and date. 

Args:
    name (str): The name of the project
    path (str): The path to the project
    date (str): The date the project was last modified
"""

from PySide2.QtCore import QAbstractListModel, Qt, QModelIndex
from models.database import ProjectDatabase

# TODO
# - Delete this file after it has been moved to data.py

class RecentProjectsModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    LocationRole = Qt.UserRole + 2
    DateRole = Qt.UserRole + 3

    def __init__(self, db_path="projects.db", parent=None):
        super().__init__(parent)
        self.db = ProjectDatabase(db_path)
        self.projects = self.db.get_projects()

    def rowCount(self, parent=QModelIndex()):
        return len(self.projects)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.projects):
            return None

        project = self.projects[index.row()]
        if role == self.NameRole:
            return project[0]
        elif role == self.LocationRole:
            return project[1]
        elif role == self.DateRole:
            return project[2]
        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.LocationRole: b"location",
            self.DateRole: b"date",
        }

    def refresh(self):
        self.beginResetModel()
        self.projects = self.db.get_projects()
        self.endResetModel()

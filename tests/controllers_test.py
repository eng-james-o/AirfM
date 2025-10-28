import json
import os
from pathlib import Path

import pytest

pytest.importorskip("PySide2")

from PySide2.QtCore import QMetaObject, QObject, QUrl
from PySide2.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide2.QtWidgets import QApplication

import globals
from models.airfoils import Airfoil_new
from models.controllers import ProjectController, airfoil_listmodel
from models.data import AirfoilListModel, RecentProjectsModel
from scripts.functions import DownloadResult


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_airfoil_file(tmp_path):
    content = """TestFoil\n1.0 0.0\n0.5 0.1\n0.0 0.0\n0.5 -0.1\n1.0 0.0\n"""
    file_path = tmp_path / "test_foil.dat"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def project_controller(tmp_path):
    db_path = tmp_path / "projects.db"
    recent_projects_model = RecentProjectsModel(db_path=str(db_path))
    controller = ProjectController(recent_projects_model=recent_projects_model)
    yield controller
    recent_projects_model.db.close()


@pytest.fixture(autouse=True)
def reset_global_airfoil_model():
    airfoil_listmodel.clear()
    yield
    airfoil_listmodel.clear()


def test_new_project_creates_structure(project_controller, tmp_path):
    project_name = "TestProject"
    project_controller.new_project(project_name, tmp_path.as_uri())

    project_dir = tmp_path / project_name
    exports_dir = project_dir / "exports"
    project_file = project_dir / f"{project_name}.afm"

    assert project_dir.exists()
    assert exports_dir.exists()
    assert project_file.exists()

    with project_file.open() as fh:
        saved = json.load(fh)
    assert saved["airfoils"] == []


def test_project_persistence_with_transformations(project_controller, tmp_path, sample_airfoil_file):
    project_controller.new_project("PersistentProject", tmp_path.as_uri())
    project_controller.add_airfoil(1, "TestFoil", str(sample_airfoil_file))

    project_controller.add_transformation(1, "translate", {"x": 0.1, "y": -0.2})

    data = project_controller.get_project_data()
    assert data["transformations"][0]["parameters"] == {"x": 0.1, "y": -0.2}
    derived = data["derived_airfoils"][0]
    assert derived["airfoil_id"] == 1
    assert derived["upper_surface"]
    assert derived["lower_surface"]

    project_file = tmp_path / "PersistentProject" / "PersistentProject.afm"
    assert project_controller.save_project(str(project_file))

    new_controller = ProjectController(recent_projects_model=None)
    new_controller.open_project(str(project_file))
    loaded = new_controller.get_project_data()
    assert loaded["transformations"] == data["transformations"]
    assert loaded["derived_airfoils"] == data["derived_airfoils"]


def test_refresh_airfoil_library_updates_model(monkeypatch, project_controller, tmp_path):
    def fake_get_save_airfoils(directory, overwrite=False, limit=None):
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)
        airfoil_file = directory_path / "generated.dat"
        airfoil_file.write_text("""Generated\n1 0\n0 0\n""")
        return DownloadResult(saved=[airfoil_file], skipped=[], errors=[])

    monkeypatch.setattr("models.controllers.get_save_airfoils", fake_get_save_airfoils)

    summary = project_controller.refresh_airfoil_library(str(tmp_path))

    assert summary["saved"] == 1
    assert summary["errors"] == []
    assert airfoil_listmodel.rowCount() == 1


def test_main_page_chart_renders_loaded_data(qapp, sample_airfoil_file, tmp_path):
    data_model = Airfoil_new()
    data_model.load(str(sample_airfoil_file))

    local_airfoil_model = AirfoilListModel()
    local_airfoil_model.addItem("TestFoil", str(sample_airfoil_file))

    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("dataModel", data_model)
    context.setContextProperty("airfoilListModel", local_airfoil_model)

    component = QQmlComponent(engine, QUrl.fromLocalFile(globals.MAIN_PAGE_QML_FILE))
    root = component.create()
    assert root is not None, component.errorString()

    chart = root.findChild(QObject, "foil_chart")
    assert chart is not None

    QMetaObject.invokeMethod(chart, "loadChartData")
    qapp.processEvents()

    series_count = chart.property("seriesCount")
    assert series_count >= 1

    root.deleteLater()

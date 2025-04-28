import pytest
from unittest.mock import MagicMock, patch
from models.controllers import AirfoilController, ProjectController
from PySide2.QtWidgets import QFileDialog

@pytest.fixture
def airfoil_controller():
    return AirfoilController()

@pytest.fixture
def project_controller():
    return ProjectController()

def test_airfoil_controller_get_airfoil_by_name(airfoil_controller):
    # Mock the data and method
    airfoil_controller.airfoil_data = {"name1": {"data": [1, 2, 3]}}

    # Test with an existing airfoil name
    result = airfoil_controller.get_airfoil_by_name("name1")
    assert result == {"data": [1, 2, 3]}

    # Test with a non-existing airfoil name
    result = airfoil_controller.get_airfoil_by_name("name2")
    assert result is None

def test_airfoil_controller_set_airfoil_by_name(airfoil_controller):
    # Test setting a new airfoil
    airfoil_controller.set_airfoil_by_name("name3", [4, 5, 6])
    assert airfoil_controller.airfoil_data["name3"] == [4, 5, 6]

    # Test overwriting an existing airfoil
    airfoil_controller.set_airfoil_by_name("name3", [7, 8, 9])
    assert airfoil_controller.airfoil_data["name3"] == [7, 8, 9]

@patch.object(QFileDialog, 'getOpenFileName')
def test_airfoil_controller_load_airfoil(mock_getOpenFileName, airfoil_controller):
    # Mock the QFileDialog to return a test file path
    mock_getOpenFileName.return_value = ("airfoils/test_airfoil.dat", "")

    # Create a test file
    with open("airfoils/test_airfoil.dat", "w") as f:
        f.write("1 1\n2 2\n3 3")

    # Test loading an airfoil
    airfoil_controller.load_airfoil()
    
    # assert airfoil_controller.airfoil_data["test_airfoil"] != None

@patch.object(QFileDialog, 'getSaveFileName')
def test_airfoil_controller_save_airfoil(mock_getSaveFileName, airfoil_controller):
    # Mock the QFileDialog to return a test file path
    mock_getSaveFileName.return_value = ("airfoils/save_test_airfoil.dat", "")

    # Set test data to be saved
    airfoil_controller.set_airfoil_by_name("test_save", [1, 2, 3])

    # Test saving the airfoil
    airfoil_controller.save_airfoil("test_save")

def test_project_controller_create_new_project(project_controller):
    # Test creating a new project
    project_controller.create_new_project("Project1")
    assert "Project1" in project_controller.projects

def test_project_controller_load_project(project_controller):
    # Mock project data
    project_data = {"Project2": {"key": "value"}}
    project_controller.projects.update(project_data)

    # Test loading an existing project
    result = project_controller.load_project("Project2")
    assert result == {"key": "value"}

    # Test loading a non-existing project
    result = project_controller.load_project("Project3")
    assert result is None

def test_project_controller_save_project(project_controller):
    # Mock project data
    project_data = {"Project3": {"key": "value"}}
    project_controller.projects.update(project_data)

    # Test saving an existing project
    project_controller.save_project("Project3")

def test_project_controller_delete_project(project_controller):
    # Mock project data
    project_data = {"Project4": {"key": "value"}}
    project_controller.projects.update(project_data)

    # Test deleting an existing project
    project_controller.delete_project("Project4")
    assert "Project4" not in project_controller.projects

    # Test deleting a non-existing project
    project_controller.delete_project("Project5") # Should not raise an error
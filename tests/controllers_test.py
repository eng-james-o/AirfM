import pytest
from unittest.mock import MagicMock, patch
from models.controllers import AirfoilController, ProjectController
from PySide2.QtWidgets import QFileDialog
import os

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

def test_new_project_creation(project_controller):
    """Test to ensure a new project is created correctly."""
    project_name = "TestProject"
    documents_folder = os.path.expanduser("~\\Documents")
    airfm_folder = os.path.join(documents_folder, "Airfm")
    project_path = os.path.join(airfm_folder, project_name)

    # Ensure the project does not already exist
    if os.path.exists(project_path):
        os.rmdir(project_path)

    project_controller.new_project(project_name)

    # Check if the project directory and files are created
    assert os.path.exists(project_path), "Project directory was not created."
    assert os.path.exists(os.path.join(project_path, "exports")), "Exports folder was not created."
    assert os.path.exists(os.path.join(project_path, f"{project_name}.afm")), \
        ".afm project file was not created."

def test_open_project(project_controller):
    """Test to ensure an existing project can be opened."""
    project_name = "TestProject"
    documents_folder = os.path.expanduser("~\\Documents")
    airfm_folder = os.path.join(documents_folder, "Airfm")
    project_path = os.path.join(airfm_folder, project_name)
    project_file_path = os.path.join(project_path, f"{project_name}.afm")

    # Create a dummy project file
    os.makedirs(project_path, exist_ok=True)
    with open(project_file_path, 'w') as f:
        f.write("{}")

    project_controller.open_project(project_file_path)

    # Check if the project data is loaded
    assert project_controller.current_project_path == project_file_path, "Project path was not set correctly."
    assert project_controller.current_project_data == {}, "Project data was not loaded correctly."

def test_save_current_project(project_controller):
    """Test to ensure the current project can be saved."""
    project_name = "TestProject"
    documents_folder = os.path.expanduser("~\\Documents")
    airfm_folder = os.path.join(documents_folder, "Airfm")
    project_path = os.path.join(airfm_folder, project_name)
    project_file_path = os.path.join(project_path, f"{project_name}.afm")

    # Create a dummy project
    os.makedirs(project_path, exist_ok=True)
    project_controller.current_project_path = project_file_path
    project_controller.current_project_data = {"test_key": "test_value"}

    project_controller.save_current_project()

    # Check if the project file is saved
    assert os.path.exists(project_file_path), "Project file was not saved."
    with open(project_file_path, 'r') as f:
        data = f.read()
    assert "test_key" in data, "Project data was not saved correctly."
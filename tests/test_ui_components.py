import pytest
from PySide2.QtCore import QUrl
from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine

@pytest.fixture(scope="module")
def app():
    """Fixture for creating the QApplication instance."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture(scope="module")
def engine():
    """Fixture for creating the QQmlApplicationEngine instance."""
    engine = QQmlApplicationEngine()
    yield engine

@pytest.fixture(scope="module")
def main_qml(engine):
    """Fixture for loading the main QML file."""
    engine.load(QUrl.fromLocalFile("qml/main.qml"))
    assert engine.rootObjects(), "Failed to load main.qml"
    return engine.rootObjects()[0]

def test_main_window_loaded(main_qml):
    """Test to ensure the main window is loaded."""
    assert main_qml is not None, "Main QML root object is None"

def test_stack_view_initial_page(main_qml):
    """Test to ensure the StackView initially displays the SelectProjectPage."""
    stack_view = main_qml.findChild(QObject, "stackView")
    assert stack_view is not None, "StackView not found in main.qml"
    assert stack_view.currentItem.objectName() == "selectProjectPage", "Initial page is not SelectProjectPage"
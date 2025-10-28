import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Item {
    id: workspace
    objectName: "projectWorkspacePage"
    implicitWidth: 880
    implicitHeight: 625

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        TabBar {
            id: workspaceTabs
            Layout.fillWidth: true

            TabButton { text: qsTr("Design") }
            TabButton { text: qsTr("Library") }
            TabButton { text: qsTr("History") }
            TabButton { text: qsTr("Acquisition") }
        }

        StackLayout {
            id: workspaceStack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: workspaceTabs.currentIndex

            Loader {
                id: designLoader
                source: Qt.resolvedUrl("MainPage.qml")
            }

            Loader {
                id: libraryLoader
                source: Qt.resolvedUrl("AirfoilLibraryPage.qml")
            }

            Loader {
                id: historyLoader
                source: Qt.resolvedUrl("TransformationHistoryPage.qml")
            }

            Loader {
                id: acquisitionLoader
                source: Qt.resolvedUrl("DataAcquisitionPage.qml")
            }
        }
    }
}

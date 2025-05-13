import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2
import "../components"

Item {
    id: selectProjectPage
    height: 625
    width: 880
    //width: parent.width
    //height: parent.height

    ColumnLayout {
        id: sideLayout
        spacing: 10

        //        anchors.bottom: parent.bottom
        //        anchors.bottomMargin: 50
        anchors {
            left: parent.left
            leftMargin: 30
            top: parent.top
            right: mainLayout.left
            topMargin: 115
        }

        TextButton {
            text: "Airfoil Library"
            Layout.minimumWidth: 120
            Layout.preferredWidth: 120
            Layout.preferredHeight: 45
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                // Logic to show airfoil library
                console.log("Show airfoil library")
            }
        }
        TextButton {
            text: "Help"
            Layout.minimumWidth: 120
            Layout.preferredWidth: 120
            Layout.preferredHeight: 45
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                // Logic to show help
                console.log("Show help")
            }
        }
    }

    ColumnLayout {
        id: mainLayout
//        width: 640
        anchors.right: parent.right
        anchors.rightMargin: 50
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        anchors.top: parent.top
        anchors.topMargin: 50
        spacing: 20

        RowLayout {
            spacing: 50

            Label {
                Layout.preferredWidth: 100
                text: "Projects"
                font.pixelSize: 24
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            TextButton {
                text: "New"
                Layout.preferredWidth: 100
                Layout.preferredHeight: 45
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    // Logic to create a new project
                    console.log("Create New Project clicked")
                    newProjectDialog.open()
                }
            }
            TextButton {
                text: "Open"
                Layout.preferredWidth: 100
                Layout.preferredHeight: 45
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    // Logic to open an existing project
                    console.log("Open Project clicked")
                    openProjectDialog.open()
                    // projectController.open(openProjectDialog.fileUrl)
                }
            }
        }

        ListView {
            id: recentProjectsList
            height: 450
            Layout.fillHeight: true
            Layout.fillWidth: true
            clip: true
            Rectangle {
                id: listviewBg
                color: "#00000000"
                radius: 5
                z: -1
                border.color: "#707070"
                border.width: 2
                anchors.fill: parent
            }

            model: recentProjectsModel

            delegate: Item {
                id: element
                width: parent.width
                height: 40

                RowLayout {
                    spacing: 10

                    Text {
                        text: model.name
                        Layout.alignment: Qt.AlignLeft
                    }

                    Text {
                        text: model.location
                        Layout.alignment: Qt.AlignLeft
                    }

                    Text {
                        text: model.date
                        Layout.alignment: Qt.AlignLeft
                    }
                }
            }
        }
    }
    FileDialog {
        id: openProjectDialog
        title: qsTr("Open Project")
        nameFilters: [ "Airfm project files (*.afm)", "Selig airfoils (*.dat)" ]
        // folder: shortcuts.Documents
        onSelectionAccepted: {
            // Logic to open the selected project
            console.log("Selected file: " + fileUrl)
            projectController.open_project(fileUrl)
        }
    }
    Dialog {
        id: newProjectDialog
        visible: false
        title: qsTr("New Project")
        width: 300
        height: 200

        Item {
            id: projectNamePage
            anchors.fill: parent

            GridLayout {
                columnSpacing: 5
                rowSpacing: 5
                columns: 2
                //spacing: 10
                anchors.fill: parent

                Label {
                    text: "Enter Project Name"
                    Layout.alignment: Qt.AlignHCenter
                    font.pixelSize: 10
                    font.bold: true
                }

                TextField {
                    id: projectNameField
                    placeholderText: "Project Name"
                    Layout.alignment: Qt.AlignHCenter
                }

                TextField {
                    id: projectLocationField
                    placeholderText: "Project Location"
                    Layout.alignment: Qt.AlignHCenter
                }

                Button {
                    text: "Choose Location"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: locationDialog.open()
                }

                Button {
                    text: "Create Project"
                    Layout.preferredWidth: 100
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        if (projectNameField.text.trim() !== "") {
                            projectController.new_project(projectNameField.text, fileUrl)
                            newProjectDialog.close()
                            console.log("Project created at: " + fileUrl)}
                        else {
                            console.log("Project name cannot be empty")
                        }
                    }
                }
            }
            FileDialog {
                id: locationDialog
                title: "Select Project Directory"
                folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
                selectFolder: true
                onAccepted: {
                    // set the projectLocationField text to the selected folder
                    projectLocationField.text = fileUrl

                }
            }
        }
    }

    // Connections {
    //     target: projectController

    //     onProjectSelected: {
    //         main_stackView.push(Qt.resolvedUrl("pages/2D_FoilPage.qml"));
    //     }
    // }
}



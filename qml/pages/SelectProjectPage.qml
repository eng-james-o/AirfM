import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import Qt.labs.platform 1.1 as Labs
import QtQuick.Dialogs 1.2 as Dialogs
import Qt.labs.settings 1.0

import "../components"

Item {
    id: selectProjectPage
    implicitHeight: 625
    implicitWidth: 880
    //    width: parent.width
    //    height: parent.height

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
    Dialogs.FileDialog {
        id: openProjectDialog
        title: qsTr("Open Project")
        nameFilters: [ "Airfm project files (*.afm)", "Selig airfoils (*.dat)" ]
        folder: shortcuts.Documents
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
        modal: true
//        width: contentItem.width + 15
//        height: contentItem.height + footer.height + 15

        footer: DialogButtonBox {
            id: buttonBox
            //            anchors.bottomMargin: 20
            spacing: 10

            Button {
                text: qsTr("Create Project")
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                onClicked: {
                    if (projectNameField.text.trim() !== "") {
                        // Logic to create a new project
                        projectController.new_project(projectNameField.text, projectLocationField.text)
                        newProjectDialog.close()
                        console.log("Project created at: " + projectLocationField.text)}
                    else {
                        console.log("Project name cannot be empty")
                    }
                }
            }

            Button {
                text: qsTr("Cancel")
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
            }
        }
        background: Rectangle {
            color: "#909090"
            radius: 10
            anchors.fill: newProjectDialog
        }

        contentItem: Item {
            id: newProjectDialogContent
            //            anchors.fill: parent
            implicitWidth: 400
            implicitHeight: 300

            Label {
                id: projectNameLabel
                text: "Enter Project Name"
                anchors.left: parent.left
                anchors.leftMargin: 15
                anchors.top: parent.top
                anchors.topMargin: 15
                // font.pixelSize: 10
            }

            TextField {
                id: projectNameField
                placeholderText: "Project Name"
                anchors.right: parent.right
                anchors.rightMargin: 15
                anchors.top: parent.top
                anchors.topMargin: 15
                anchors.left: projectNameLabel.right
                anchors.leftMargin: 15
            }

            Label {
                id: projectLocationLabel
                text: "Select Project Location"
                anchors.left: parent.left
                anchors.leftMargin: 15
                anchors.top: projectNameField.bottom
                anchors.topMargin: 15
                // font.pixelSize: 10
            }

            TextField {
                id: projectLocationField
                placeholderText: "Project Location"
                anchors.left: projectLocationLabel.right
                anchors.leftMargin: 15
                anchors.top: projectNameField.bottom
                anchors.topMargin: 15
                readOnly: true
            }

            Button {
                text: "Browse Location"
                anchors.left: projectLocationField.right
                anchors.leftMargin: 15
                anchors.top: projectLocationField.top
                anchors.right: parent.right
                anchors.rightMargin: 15
                onClicked: locationDialog.open()
            }
            Label {
                id: projectSummaryLabel
                text: "Project summary"
                anchors.left: parent.left
                anchors.top: projectLocationField.bottom
                anchors.leftMargin: 15
                anchors.topMargin: 15
            }
            TextArea {
                id: projectSummaryField
                anchors.left: projectSummaryLabel.right
                anchors.top: projectLocationField.bottom
                anchors.right: parent.right
                anchors.margins: 15
                placeholderText: "Enter additional project details"
            }

            Dialogs.FileDialog {
                id: locationDialog
                title: "Select Project Directory"
                // folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
                folder: shortcuts.home
                selectFolder: true
                onAccepted: {
                    // set the projectLocationField text to the selected folder
                    projectLocationField.text = fileUrl
                }
            }
        }
    }
}



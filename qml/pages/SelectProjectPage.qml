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
            Layout.preferredWidth: 100
            Layout.preferredHeight: 45
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                // Logic to show airfoil library
                console.log("Show airfoil library")
            }
        }
        TextButton {
            text: "Help"
            Layout.preferredWidth: 100
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
        width: 640
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

            model: ListModel {
                ListElement { name: "Project 1"; location:"C:/Users"; date:"12-16-25" }
                ListElement { name: "Project 2"; location:"C:/Users"; date:"12-16-25" }
                ListElement { name: "Project 3"; location:"C:/Users"; date:"12-16-25" }
            }

            delegate: Item {
                id: element
                width: parent.width
                height: 40

                Rectangle {
                    id: rectangle
                    width: parent.width - 20
                    height: parent.height - 4
                    color: "#f0f0f0"
                    border.color: "#cccccc"
                    radius: 5
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.left: parent.left
                        text: model.name
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        font.pixelSize: 18
                    }
                    Text {
                        anchors.centerIn: parent
                        text: model.location
                        font.pixelSize: 18
                    }
                    Text {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        text: model.date
                        anchors.rightMargin: 10
                        font.pixelSize: 18
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            // Logic to open the selected project
                            console.log("Selected project: " + model.name)
                        }
                    }
                }
            }
        }
    }
    FileDialog {
        id: openProjectDialog
        title: qsTr("Open Project")
        nameFilters: [ "Airfm project files (*.afm)", "Selig airfoils (*.dat)" ]
        folder: shortcuts.Documents
        onSelectionAccepted: {
            //openProjectDialog.file
        }
    }
    Dialog {
        id: newProjectDialog
        title: qsTr("New Project")

        StackView {
            id: stack
            anchors.fill: parent

            initialItem: Page {
                id: projectNamePage

                ColumnLayout {
                    spacing: 10
                    anchors.fill: parent

                    Label {
                        text: "Enter Project Name"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    TextField {
                        id: projectNameField
                        placeholderText: "Project Name"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Button {
                        text: "Next"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: {
                            if (projectNameField.text.trim() !== "") {
                                stack.push(projectLocationPage)
                            } else {
                                console.log("Project name cannot be empty")
                            }
                        }
                    }
                }
            }

            Component {
                id: projectLocationPage

                Page {
                    id: locationPage

                    ColumnLayout {
                        spacing: 10
                        anchors.fill: parent

                        Label {
                            text: "Select Project Location"
                            Layout.alignment: Qt.AlignHCenter
                        }

                        FileDialog {
                            id: locationDialog
                            title: "Select Project Directory"
                            folder: shortcuts.Documents
                            selectFolder: true
                            onAccepted: {
                                projectController.new_project(projectNameField.text, fileUrl)
                                newProjectDialog.close()
                            }
                        }

                        Button {
                            text: "Choose Location"
                            Layout.alignment: Qt.AlignHCenter
                            onClicked: locationDialog.open()
                        }

                        Button {
                            text: "Back"
                            Layout.alignment: Qt.AlignHCenter
                            onClicked: stack.pop()
                        }
                    }
                }
            }
        }
    }
}


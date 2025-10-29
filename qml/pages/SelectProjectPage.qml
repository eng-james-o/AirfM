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
    objectName: "selectProjectPage"
    property string libraryStatus: ""
    //    width: parent.width
    //    height: parent.height

    SwipeView {
        id: selectionSwipeView
        anchors.fill: parent
        // interactive: true
        interactive: false

        Item {
            id: projectOverviewPage
            width: selectionSwipeView.width
            height: selectionSwipeView.height

            ColumnLayout {
                id: sideLayout
                anchors.rightMargin: 30
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
                    onClicked: selectionSwipeView.currentIndex = 1
                }
                TextButton {
                    text: "Refresh Library"
                    Layout.minimumWidth: 120
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 45
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        const summary = projectController.refresh_airfoil_library()
                        if (summary.errors.length > 0) {
                            libraryStatus = "Downloaded " + summary.saved + ", skipped " + summary.skipped + ", errors: " + summary.errors.join(", ")
                        } else {
                            libraryStatus = "Downloaded " + summary.saved + ", skipped " + summary.skipped
                        }
                    }
                }
                Text {
                    text: libraryStatus
                    wrapMode: Text.WordWrap
                    Layout.alignment: Qt.AlignHCenter
                    Layout.maximumWidth: 160
                    color: libraryStatus.indexOf("errors:") >= 0 ? "#ff6666" : "#21be2b"
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
                width: 600
                //        width: 640
                anchors.right: parent.right
                anchors.rightMargin: 30
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 50
                anchors.top: parent.top
                anchors.topMargin: 50
                spacing: 20

                RowLayout {
                    spacing: 50

                    Label {
                        color: "#ddffffff"
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
                        height: 56
                        property bool hovered: false

                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 4
                            radius: 6
                            color: hovered ? "#2d3348" : "transparent"
                            border.color: hovered ? "#4c9ffe" : "transparent"
                            border.width: hovered ? 1 : 0
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Label {
                                text: model.name
                                font.bold: true
                                color: "#f5f5f5"
                                Layout.preferredWidth: 160
                            }

                            Label {
                                text: model.path
                                color: "#cbd5f5"
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }

                            Label {
                                text: model.date
                                color: "#94a3b8"
                                Layout.preferredWidth: 170
                                horizontalAlignment: Text.AlignRight
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onEntered: element.hovered = true
                            onExited: element.hovered = false
                            onClicked: {
                                projectController.open_project(model.path)
                        }
                    }
                }

                Label {
                    visible: recentProjectsModel && recentProjectsModel.count === 0
                    text: qsTr("Recently opened projects will appear here.")
                    color: "#94a3b8"
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    Dialog {
        id: newProjectDialog
        visible: false
        title: qsTr("New Project")
        modal: true

        x: (parent.width - width) / 2
        y: (parent.height - height) / 2

        width: newProjectDialogContent.width + 10 //contentItem.width + 15
        height: newProjectDialogContent.height + footer.height + 10 //contentItem.height + header.height + footer.height + 15
        dim: true

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
            color: "#9296a0"
            radius: 10
            anchors.fill: newProjectDialog
        }

        Item {
            id: newProjectDialogContent
            //            anchors.fill: parent
            implicitWidth: 550
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
                height: 60
                anchors.left: projectSummaryLabel.right
                anchors.top: projectLocationField.bottom
                anchors.right: parent.right
                anchors.margins: 15
                placeholderText: "Enter additional project details"
            }

        }
    } // closes newProjectDialog
}

        Item {
            id: librarySwipePage
            width: selectionSwipeView.width
            height: selectionSwipeView.height

            Loader {
                id: libraryLoader
                anchors.fill: parent
                source: Qt.resolvedUrl("AirfoilLibraryPage.qml")
                active: selectionSwipeView.currentIndex === 1
            }

            TextButton {
                text: qsTr("Back to Projects")
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: 20
                onClicked: selectionSwipeView.currentIndex = 0
            }
        }
    }

    Dialogs.FileDialog {
        id: openProjectDialog
        title: qsTr("Open Project")
        nameFilters: [ "Airfm project files (*.afm)", "Selig airfoils (*.dat)" ]
        folder: shortcuts.Documents
        onSelectionAccepted: {
            console.log("Selected file: " + fileUrl)
            projectController.open_project(fileUrl)
        }
    }

    Dialogs.FileDialog {
        id: locationDialog
        title: qsTr("Select Project Directory")
        // folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        folder: shortcuts.home
        selectFolder: true
        onAccepted: projectLocationField.text = fileUrl
    }
}


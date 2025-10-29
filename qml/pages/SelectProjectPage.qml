import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12
import Qt.labs.platform 1.1 as Labs
import QtQuick.Dialogs 1.2 as Dialogs

import "../components"

Item {
    id: selectProjectPage
    implicitHeight: 625
    implicitWidth: 880
    objectName: "selectProjectPage"
    property string libraryStatus: ""

    function localPathToUrl(path) {
        if (!path)
            return ""
        var normalized = path.replace(/\\/g, "/")
        if (normalized.indexOf("file:/") === 0)
            return normalized
        return "file:///" + normalized
    }

    property url documentsFolder: localPathToUrl(Labs.StandardPaths.writableLocation(Labs.StandardPaths.DocumentsLocation))
    property url homeFolder: localPathToUrl(Labs.StandardPaths.writableLocation(Labs.StandardPaths.HomeLocation))

    SwipeView {
        id: selectionSwipeView
        anchors.fill: parent
        interactive: false

        Item {
            id: projectOverviewPage
            width: selectionSwipeView.width
            height: selectionSwipeView.height

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 30
                anchors.rightMargin: 30
                anchors.topMargin: 50
                anchors.bottomMargin: 40
                spacing: 40

                ColumnLayout {
                    id: sideLayout
                    Layout.preferredWidth: 200
                    Layout.fillHeight: true
                    spacing: 12

                    TextButton {
                        text: qsTr("Airfoil Library")
                        Layout.fillWidth: true
                        Layout.preferredHeight: 45
                        onClicked: selectionSwipeView.currentIndex = 1
                    }

                    TextButton {
                        text: qsTr("Refresh Library")
                        Layout.fillWidth: true
                        Layout.preferredHeight: 45
                        onClicked: {
                            const summary = projectController.refresh_airfoil_library()
                            if (summary.errors.length > 0) {
                                libraryStatus = qsTr("Downloaded %1, skipped %2, errors: %3")
                                                    .arg(summary.saved)
                                                    .arg(summary.skipped)
                                                    .arg(summary.errors.join(", "))
                            } else {
                                libraryStatus = qsTr("Downloaded %1, skipped %2")
                                                    .arg(summary.saved)
                                                    .arg(summary.skipped)
                            }
                        }
                    }

                    Text {
                        text: libraryStatus
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        color: libraryStatus.indexOf("errors:") >= 0 ? "#ff6666" : "#21be2b"
                    }

                    Item { Layout.fillHeight: true }

                    TextButton {
                        text: qsTr("Help")
                        Layout.fillWidth: true
                        Layout.preferredHeight: 45
                        onClicked: console.log("Show help")
                    }
                }

                ColumnLayout {
                    id: mainLayout
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 20

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Label {
                            text: qsTr("Projects")
                            font.pixelSize: 24
                            color: "#ddffffff"
                        }

                        Item { Layout.fillWidth: true }

                        TextButton {
                            text: qsTr("New")
                            Layout.preferredWidth: 100
                            Layout.preferredHeight: 45
                            onClicked: {
                                console.log("Create New Project clicked")
                                newProjectDialog.open()
                            }
                        }

                        TextButton {
                            text: qsTr("Open")
                            Layout.preferredWidth: 100
                            Layout.preferredHeight: 45
                            onClicked: {
                                console.log("Open Project clicked")
                                openProjectDialog.open()
                            }
                        }
                    }

                    ListView {
                        id: recentProjectsList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 4

                        Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: "transparent"
                            border.color: "#2d3348"
                            border.width: 1
                            z: -1
                        }

                        model: recentProjectsModel

                        delegate: Item {
                            id: element
                            width: recentProjectsList.width
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
                                onClicked: projectController.open_project(model.path)
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

    Dialog {
        id: newProjectDialog
        title: qsTr("Create Project")
        modal: true
        dim: true
        focus: true
        padding: 24
        x: (selectProjectPage.width - implicitWidth) / 2
        y: (selectProjectPage.height - implicitHeight) / 2

        background: Rectangle {
            radius: 14
            color: "#1e2336"
            border.color: "#3b4366"
            border.width: 1
            layer.enabled: true
            layer.effect: DropShadow {
                horizontalOffset: 0
                verticalOffset: 6
                radius: 18
                samples: 25
                color: "#80000000"
            }
        }

        contentItem: ColumnLayout {
            id: newProjectDialogContent
            spacing: 14
            width: 520

            Label {
                text: qsTr("Project Details")
                font.pixelSize: 20
                font.bold: true
                color: "#f8fafc"
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: qsTr("Project Name")
                color: "#94a3b8"
            }

            TextField {
                id: projectNameField
                placeholderText: qsTr("Enter a project name")
                Layout.fillWidth: true
            }

            Label {
                text: qsTr("Project Location")
                color: "#94a3b8"
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                TextField {
                    id: projectLocationField
                    placeholderText: qsTr("Choose where the project will be stored")
                    Layout.fillWidth: true
                    readOnly: true
                }

                TextButton {
                    text: qsTr("Browse")
                    Layout.preferredWidth: 110
                    onClicked: locationDialog.open()
                }
            }

            Label {
                text: qsTr("Project Summary (optional)")
                color: "#94a3b8"
            }

            TextArea {
                id: projectSummaryField
                placeholderText: qsTr("Add any context or goals for this project")
                Layout.fillWidth: true
                Layout.preferredHeight: 100
            }
        }

        footer: DialogButtonBox {
            alignment: Qt.AlignRight
            spacing: 12

            Button {
                text: qsTr("Cancel")
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
            }

            Button {
                text: qsTr("Create Project")
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                onClicked: {
                    if (projectNameField.text.trim() !== "") {
                        projectController.new_project(projectNameField.text, projectLocationField.text)
                        newProjectDialog.close()
                        console.log("Project created at: " + projectLocationField.text)
                    } else {
                        console.log("Project name cannot be empty")
                    }
                }
            }
        }
    }

    Dialogs.FileDialog {
        id: openProjectDialog
        title: qsTr("Open Project")
        nameFilters: [ "Airfm project files (*.afm)", "Selig airfoils (*.dat)" ]
        folder: documentsFolder
        onSelectionAccepted: {
            console.log("Selected file: " + fileUrl)
            projectController.open_project(fileUrl)
        }
    }

    Dialogs.FileDialog {
        id: locationDialog
        title: qsTr("Select Project Directory")
        folder: homeFolder
        selectFolder: true
        onAccepted: projectLocationField.text = fileUrl
    }
}

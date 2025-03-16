import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import "../components"

Item {
    id: selectProjectPage
    height: 625
    width: 880
    //width: parent.width
    //height: parent.height

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        Text {
            text: "Select or Create Project"
            font.pixelSize: 24
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }

        TextButton {
            text: "New"
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                // Logic to create a new project
                console.log("Create New Project clicked")
            }
        }
        TextButton {
            text: "Open"
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                // Logic to create a new project
                console.log("Open Project clicked")
            }
        }

        ListView {
            id: recentProjectsList
            width: parent.width * 0.8
            height: parent.height * 0.5
            model: ListModel {
                ListElement { name: "Project 1" }
                ListElement { name: "Project 2" }
                ListElement { name: "Project 3" }
            }

            delegate: Item {
                width: parent.width
                height: 50

                Rectangle {
                    width: parent.width
                    height: parent.height
                    color: "#f0f0f0"
                    border.color: "#cccccc"
                    radius: 5

                    Text {
                        anchors.centerIn: parent
                        text: model.name
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
}


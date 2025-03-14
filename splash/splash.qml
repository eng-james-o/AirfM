import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import "../qml/components"

Window {
    id: splash_screen
    width: 640
    height: 480
    visible: true

    // Remove title bar
    flags: Qt.Window | Qt.FramelessWindowHint

    Item {
        id: brand
        anchors.centerIn: parent
        width: name.width + image.width
        height: Math.max(name.height, image.height)

        Label {
            id: name
            text: qsTr("AirfM")
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
        }
        Image {
            id: image
            width: 50
            height: 50
            anchors.left: name.right
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            source: "../assets/svg_images/airfoil.svg"
//            source: "qrc:/svg/svg_images/airfoil.svg"
        }
    }

    ProgressBar {
        id: progressBar
        y: 370
        width: 600
        height: 40
        anchors.horizontalCenter: parent.horizontalCenter
        //        value: 0.5
        indeterminate: true
        //        padding: 2

        background: Rectangle {
            width: parent.width
            height: parent.height
            color: "#B5BBFF"
            radius: 10
        }

        contentItem: Item {
            //            implicitWidth: 200
            //            implicitHeight: 4

            Rectangle {
                width: progressBar.visualPosition * parent.width
                height: parent.height
                radius: 7.5
                color: "#2C3BFF"
            }
        }
    }
    Label {
        id: staticText
        text: qsTr("Progress:")
        anchors.left: progressBar.left
        anchors.bottom: progressBar.top
    }
    Label {
        id: progressbarText
        text: qsTr("Assessing imports")
        anchors.left: staticText.right
        anchors.leftMargin: 5
        anchors.bottom: progressBar.top
    }
}



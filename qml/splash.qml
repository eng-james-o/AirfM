import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtCharts 2.12
import "../qml/components"

Window {
    id: splashScreen
    width: 640
    height: 480
    color: "#a2a2a2"
    visible: true
    title: qsTr("AirfM")

    // Remove title bar
    flags: Qt.SplashScreen | Qt.FramelessWindowHint
    // modality: Qt.ApplicationModal

    WindowButton {
        id: closeButton
        btnIconSource: "../assets/svg_images/close_icon.svg"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        width: 40
        height: 40
        btnColorClicked: "#55aaff"
        btnColorMouseOver: "#ff1515"
        btnColorDefault: "#00000000" //"#902020"
        btnColorOverlay: "#262626"

        CustomToolTip {
            text: "Quit"
        }
        onPressed: splashScreen.close()
    }
    Item {
        id: brand
        anchors.centerIn: parent
        width: name.width + image.width
        height: Math.max(name.height, image.height)

        Label {
            id: name
            text: qsTr("AirfM")
            font.bold: true
            font.pointSize: 12
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
        }
        Image {
            id: image
            width: 80
            height: 80
            anchors.leftMargin: -10
            anchors.left: name.right
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            source: "../assets/svg_images/airfoil.svg"
        }
    }
    ProgressBar {
        id: progressBar
        y: 370

        width: 600
        height: 10
        padding: 1
        anchors.horizontalCenter: parent.horizontalCenter
        value: 0
        from: 0; to: 3

        Behavior on value {
            NumberAnimation {
                duration: 500
                easing.type: Easing.OutQuad
            }
        }
        background: Rectangle {
            width: parent.width
            height: parent.height
            color: "#B5BBFF"
            radius: 10
        }

        contentItem: Item {
            width: parent.width
            height: parent.height

            Rectangle {
                width: progressBar.visualPosition * (parent.width - 2*progressBar.padding)
                x: progressBar.padding
                y: progressBar.padding
                height: parent.height - 2 * progressBar.padding
                radius: 7.5
                color: "#2C3BFF"
            }
        }
    }
    Label {
        id: staticText
        text: qsTr("Progress:")
        anchors.bottomMargin: 15
        font.pointSize: 7
        anchors.left: progressBar.left
        anchors.bottom: progressBar.top
    }
    Label {
        id: progressbarText
        text: qsTr("")
        font.pointSize: 7
        width: 545
        anchors.left: staticText.right
        anchors.leftMargin: 5
        anchors.bottom: progressBar.top
        anchors.bottomMargin: 15
        wrapMode: Text.WrapAnywhere
    }

    signal reLoadingProgress (int number, string step)
    
    Component.onCompleted: {
        splashController.loadingProgress.connect(reLoadingProgress)
        splashController.initialise_app()
    }

    Connections {
        target: splashScreen
        function onReLoadingProgress (number, text) {
            progressBar.value = number
            progressbarText.text = text
            // console.log(progressBar.value, step)
        }
    }
}

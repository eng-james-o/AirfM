import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

Button{
    id: btnTopBar
    // CUSTOM PROPERTIES
    property url btnIconSource: "../../assets/svg_images/minimize_icon.svg"
    property color btnColorDefault: "#00000000"
    property color btnColorMouseOver: "#40265d"
    property color btnColorClicked: "#00a1f1"
    property color btnColorOverlay: "#ffffff"
    property int btnRadius: 16

    QtObject{
        id: internal

        // MOUSE OVER AND CLICK CHANGE COLOR
        property var dynamicColor: if(btnTopBar.down){
                                       btnTopBar.down ? btnColorClicked : btnColorDefault
                                   } else {
                                       btnTopBar.hovered ? btnColorMouseOver : btnColorDefault
                                   }
    }

    width: 35
    height: 35

    background: Rectangle{
        id: bgBtn
        color: internal.dynamicColor
        radius: btnRadius
        anchors.fill: parent
        anchors.margins: 3

        Image {
            // icon on the button
            id: iconBtn
            source: btnIconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 16
            width: 16
            visible: false
            fillMode: Image.PreserveAspectFit
            antialiasing: false
        }

        ColorOverlay{
            anchors.fill: iconBtn
            source: iconBtn
            color: btnColorOverlay
            antialiasing: false
        }
    }
}



import QtQuick 2.12
import QtQuick.Controls 2.12
// import QtGraphicalEffects 1.12

Button {
    id: button

    // Custom Properties
    property color colorDefault: "#4891d9"
    property color colorMouseOver: "#55AAFF"
    property color colorPressed: "#3F7EBD"
    property color textColor: "#000000"
    property color borderColor: textColor

    text: qsTr("Button")
    width: 50
    implicitWidth: 50
    height: 25
    implicitHeight: 25

    QtObject{
        id: internal

        property var dynamicColor: if(button.down){
                                       button.down ? colorPressed : colorDefault
                                   }else{
                                       button.hovered ? colorMouseOver : colorDefault
                                   }
    }

    contentItem: Item{
        anchors.fill: parent

        Text {
            id: name
            text: button.text
            font: button.font
            color: textColor
            anchors.centerIn: parent
        }
    }

    background: Rectangle{
        id: bg
        color: internal.dynamicColor
        anchors.fill: parent
        radius: 5
        border.color: button.borderColor
        border.width: 2
    }
}


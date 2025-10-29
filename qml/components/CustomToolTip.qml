import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

ToolTip{
    id: control
    visible: parent.hovered
    delay: 500
    timeout: 3000
    text: qsTr("Tooltip text")
    rightPadding: 10
    leftPadding: 10

    contentItem: Text{
        text: control.text
        font: control.font
        color: "#d9dce1"
    }

    background: Rectangle{
        color: "#222327"
        border.color: "#36373d"
        border.width: 1
        radius: 5
    }
}

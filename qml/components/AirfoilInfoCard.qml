import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Frame {
    id: root
    property string title: ""
    property string subtitle: ""
    property string description: ""
    property url fileUrl: ""

    background: Rectangle {
        radius: 12
        color: "#ffffff"
        border.color: "#a0aec0"
        border.width: 1
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 4

        Label {
            text: title
            font.pixelSize: 18
            font.bold: true
        }

        Label {
            text: subtitle
            font.pixelSize: 12
            color: "#4a5568"
        }

        Label {
            text: description
            wrapMode: Text.Wrap
            color: "#2d3748"
            Layout.fillWidth: true
        }

        Label {
            visible: fileUrl !== ""
            text: qsTr("Path: %1").arg(fileUrl)
            font.family: "Monospace"
            font.pixelSize: 10
            color: "#718096"
            wrapMode: Text.Wrap
        }
    }
}

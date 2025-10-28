import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Rectangle {
    id: root
    property var summary: ({})
    property color borderColor: summary.errors && summary.errors.length > 0 ? "#d9534f" : "#3c763d"
    radius: 8
    color: "#f8f9fa"
    border.color: borderColor
    border.width: 2
    implicitWidth: 220
    implicitHeight: contentColumn.implicitHeight + 16

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        Label {
            text: qsTr("Download summary")
            font.bold: true
            Layout.fillWidth: true
        }

        Label {
            text: summary && summary.directory ? qsTr("Directory: %1").arg(summary.directory) : qsTr("Directory: -")
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 4
            Layout.fillWidth: true

            Label { text: qsTr("Saved:") }
            Label { text: summary && summary.saved !== undefined ? summary.saved : "-" }

            Label { text: qsTr("Skipped:") }
            Label { text: summary && summary.skipped !== undefined ? summary.skipped : "-" }

            Label { text: qsTr("Errors:") }
            Label {
                text: summary && summary.errors ? summary.errors.length : "0"
                color: summary && summary.errors && summary.errors.length > 0 ? "#d9534f" : "#212529"
            }
        }

        Repeater {
            model: summary && summary.errors ? summary.errors : []
            delegate: Label {
                text: "• " + modelData
                color: "#d9534f"
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }
        }
    }
}

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

import "../components"

Item {
    id: historyPage
    objectName: "transformationHistoryPage"
    implicitWidth: 880
    implicitHeight: 625

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        Label {
            text: qsTr("Transformation History")
            font.pixelSize: 24
        }

        Label {
            text: qsTr("Track every operation applied to the airfoils in the active project.")
            color: "#4a5568"
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 12
            color: "#f8fafc"
            border.color: "#cbd5e0"
            border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 12

                TransformationList {
                    width: parent.width - 24
                    model: airfoilActionModel
                }
            }
        }
    }
}

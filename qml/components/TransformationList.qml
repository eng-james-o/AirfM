import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Item {
    id: root
    implicitWidth: listView.implicitWidth
    implicitHeight: listView.implicitHeight
    property alias model: listView.model

    ListView {
        id: listView
        anchors.fill: parent
        clip: true
        spacing: 8

        delegate: Frame {
            width: ListView.view.width
            background: Rectangle {
                radius: 10
                color: "#f5f7fb"
                border.color: "#a0b4d8"
                border.width: 1
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6

                Label {
                    text: model.name
                    font.bold: true
                    font.pixelSize: 16
                }

                Label {
                    text: qsTr("Airfoil ID: %1").arg(model.id)
                    color: "#4a5568"
                }

                Repeater {
                    model: model.transformations || []
                    delegate: Rectangle {
                        color: "#ffffff"
                        radius: 6
                        border.color: "#cbd5e0"
                        border.width: 1
                        Layout.fillWidth: true
                        implicitHeight: detailsRow.implicitHeight + 10

                        RowLayout {
                            id: detailsRow
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            Label {
                                text: qsTr("Type: %1").arg(modelData.type || "-")
                                Layout.fillWidth: true
                                font.bold: true
                            }

                            Label {
                                text: JSON.stringify(modelData.parameters || {})
                                font.family: "Monospace"
                                color: "#2d3748"
                                Layout.fillWidth: true
                                wrapMode: Text.Wrap
                            }
                        }
                    }
                }

                Label {
                    visible: !(model.transformations && model.transformations.length)
                    text: qsTr("No transformations recorded.")
                    color: "#6c757d"
                }
            }
        }
    }
}

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

import "../components"

Item {
    id: libraryPage
    objectName: "airfoilLibraryPage"
    implicitWidth: 880
    implicitHeight: 625

    property var lastSummary: ({})

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            TextButton {
                text: qsTr("Back")
                Layout.preferredWidth: 100
                Layout.preferredHeight: 40
                visible: StackView.view && StackView.view.depth > 1
                onClicked: {
                    if (StackView.view) {
                        StackView.view.pop()
                    }
                }
            }

            Label {
                text: qsTr("Airfoil Library")
                font.pixelSize: 24
                Layout.fillWidth: true
            }

            TextButton {
                id: refreshButton
                text: qsTr("Refresh")
                Layout.preferredWidth: 120
                Layout.preferredHeight: 40
                onClicked: {
                    lastSummary = projectController.refresh_airfoil_library()
                }
            }
        }

        DownloadStatusCard {
            Layout.fillWidth: true
            summary: libraryPage.lastSummary
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 12
            color: "#f1f4f8"
            border.color: "#cbd5e0"
            border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 12
                clip: true

                ColumnLayout {
                    id: listColumn
                    width: parent.width - 24
                    spacing: 12

                    Repeater {
                        model: airfoilListModel
                        delegate: AirfoilInfoCard {
                            Layout.fillWidth: true
                            title: model.name
                            subtitle: qsTr("Available in library")
                            description: qsTr("Airfoil geometry ready for loading and transformation workflows.")
                            fileUrl: model.path
                        }
                    }

                    Label {
                        visible: airfoilListModel.rowCount() === 0
                        text: qsTr("No airfoils found. Use the refresh button to download the UIUC archive.")
                        wrapMode: Text.Wrap
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                        color: "#6c757d"
                        Layout.preferredWidth: parent.width * 0.7
                    }
                }
            }
        }
    }
}

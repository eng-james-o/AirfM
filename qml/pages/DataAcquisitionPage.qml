import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2 as Dialogs
import Qt.labs.platform 1.1 as Labs

import "../components"

Item {
    id: acquisitionPage
    objectName: "dataAcquisitionPage"
    implicitWidth: 880
    implicitHeight: 625

    property string targetDirectory: ""
    property bool overwriteExisting: false
    property int downloadLimit: -1
    property var lastSummary: ({})

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        Label {
            text: qsTr("UIUC Data Acquisition")
            font.pixelSize: 24
        }

        Label {
            text: qsTr("Pull the latest airfoil coordinate files directly into the workspace and keep the project library up to date.")
            wrapMode: Text.Wrap
            color: "#4a5568"
            Layout.fillWidth: true
        }

        GridLayout {
            columns: 3
            columnSpacing: 12
            rowSpacing: 8
            Layout.fillWidth: true

            Label { text: qsTr("Target directory") }
            TextField {
                id: directoryField
                Layout.fillWidth: true
                text: acquisitionPage.targetDirectory
                placeholderText: qsTr("Leave empty to use the default library path")
                onEditingFinished: acquisitionPage.targetDirectory = text
            }
            TextButton {
                text: qsTr("Browse")
                Layout.preferredWidth: 100
                onClicked: directoryDialog.open()
            }

            Label { text: qsTr("Overwrite existing") }
            Switch {
                id: overwriteSwitch
                checked: acquisitionPage.overwriteExisting
                onToggled: acquisitionPage.overwriteExisting = checked
            }
            Item { }

            Label { text: qsTr("Limit downloads") }
            SpinBox {
                id: limitSpin
                from: -1
                to: 500
                value: acquisitionPage.downloadLimit
                onValueChanged: acquisitionPage.downloadLimit = value
                stepSize: 10
                validator: IntValidator { bottom: -1 }
            }
            Label {
                text: qsTr("-1 downloads everything")
                color: "#718096"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            TextButton {
                text: qsTr("Start Download")
                Layout.preferredWidth: 160
                onClicked: {
                    const limitValue = acquisitionPage.downloadLimit
                    if (limitValue === -1) {
                        acquisitionPage.lastSummary = projectController.refresh_airfoil_library(acquisitionPage.targetDirectory, acquisitionPage.overwriteExisting)
                    } else {
                        acquisitionPage.lastSummary = projectController.refresh_airfoil_library(acquisitionPage.targetDirectory, acquisitionPage.overwriteExisting, limitValue)
                    }
                }
            }

            Label {
                text: acquisitionPage.lastSummary && acquisitionPage.lastSummary.saved !== undefined
                      ? qsTr("Last updated: saved %1, skipped %2").arg(acquisitionPage.lastSummary.saved).arg(acquisitionPage.lastSummary.skipped)
                      : qsTr("No downloads yet.")
                color: "#2d3748"
                Layout.fillWidth: true
            }
        }

        DownloadStatusCard {
            Layout.fillWidth: true
            summary: acquisitionPage.lastSummary
        }
    }

    Dialogs.FileDialog {
        id: directoryDialog
        title: qsTr("Select download folder")
        folder: Labs.StandardPaths.writableLocation(Labs.StandardPaths.DocumentsLocation)
        selectFolder: true
        onAccepted: {
            acquisitionPage.targetDirectory = fileUrl
            directoryField.text = fileUrl
        }
    }
}

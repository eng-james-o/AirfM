import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle{
    property int appBarRadius: 10
    property color appBarbg: "#33334c"

    implicitWidth: 800
    height: 50
    radius: appBarRadius
    id: app_bar
    border.color: "#838460"
    border.width: 2
    color: appBarbg

    DragHandler { onActiveChanged: if(active){
                                       mainWindow.startSystemMove()
                                       internal.ifMaximizedWindowRestore()
                                   }
    }

    Rectangle {

        id: top_tool_bar
        anchors.fill: parent
        anchors.margins: 5
        color: appBarbg

        Image {
            id: app_icon
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            source: "../../assets/airfoil.png"

            /*Image {
                id: name
                source: "file"
                // show small arrow onEntered
            }*/

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor

                onClicked: {
                    animationMenu.running = true
                    /*if(topMenu.width === 0){
                            btnSettings.btnIconSource = "../images/svg_images/close_icon_2.svg"
                            settingsTooltip.text = "Hide settings"
                        } else {
                            btnSettings.btnIconSource = "../images/svg_images/settings_icon.svg"
                            settingsTooltip.text = "Account configurations"
                        }*/
                }
            }
        }

        Rectangle {
            id: topMenu
            width: 0
            height: 40
            //radius: 5
            color: "transparent"
            border.width: 0
            anchors.left: app_icon.right

            anchors.verticalCenter: parent.verticalCenter
            clip: true

            PropertyAnimation{
                id: animationMenu
                target: topMenu
                property: "width"
                to: if(topMenu.width == 0) return 240; else return 0
                duration: 800
                easing.type: Easing.InOutQuint
            }

            CustomButton {
                id: file_btn
                width: 80
                height: 40
                text: "File"
                anchors.left: topMenu.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 10
                colorDefault: "#2d2d3b"
            }
            CustomButton {
                width: 80
                height: 40
                text: "Analyse"
                anchors.left: file_btn.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 10
                colorDefault: "#2d2d3b"
            }
        }

        TopBarButton {
            id: closeButton
            btnIconSource: "../../assets/svg_images/close_icon.svg"
            anchors.right: top_tool_bar.right
            anchors.verticalCenter: top_tool_bar.verticalCenter
            width: 40
            btnColorClicked: "#55aaff"
            btnColorMouseOver: "#ff007f"
            CustomToolTip {
                text: "Close"
            }
            onPressed: mainWindow.close()
        }
        TopBarButton {
            id: maxButton
            btnIconSource: "../../assets/svg_images/maximize_icon.svg"
            anchors.right: closeButton.left
            anchors.verticalCenter: top_tool_bar.verticalCenter
            width: 40
            btnColorMouseOver: "#40405f"
            btnColorClicked: "#55aaff"
            CustomToolTip {
                text: "Maximize"
            }
            onClicked: internal.maximizeRestore()
        }
        TopBarButton {
            id: minButton
            btnIconSource: "../../assets/svg_images/minimize_icon.svg"
            anchors.right: maxButton.left
            anchors.verticalCenter: top_tool_bar.verticalCenter
            width: 40
            btnRadius: 17
            btnColorClicked: "#55aaff"
            btnColorMouseOver: "#40405f"
            CustomToolTip {
                text: "Minimize"
            }
            onClicked: {
                mainWindow.showMinimized()
                internal.restoreMargins()
            }
        }

    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.33}
}
##^##*/

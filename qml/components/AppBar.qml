import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

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
            source: "../../assets/svg_images/airfoil.svg"

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

            MenuBar {
                id: menubar
                Menu {
                    title: "File"
                    Action {
                        text: "New"
                        onTriggered: console.log("New clicked")
                    }
                    Action {
                        text: "Open"
                        onTriggered: console.log("Open clicked")
                    }
                    Action {
                        text: "Save"
                        onTriggered: {
                            projectController.save_current_project()
                        }
                    }
                    Action {
                        text: "Exit"
                        onTriggered: Qt.quit()
                    }
                    Action {
                        text: "Export airfoil"
                        onTriggered: console.log("Export")
                    }
                }
                Menu {
                    title: "Analyse"
                }
            }
        }

        WindowButton {
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
        WindowButton {
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
        WindowButton {
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

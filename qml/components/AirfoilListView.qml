import QtQuick 2.12
import QtQuick.Controls 2.12
//import QtQuick.Controls.Material 2.12
import QtQuick.Layouts 1.12

Item {
    id: topLevel
    width: 200
    height: 400

    Item {
        id: airfoilsColumn
        width: parent.width - 10
        anchors.horizontalCenter: parent.horizontalCenter
//        spacing: 15 // Spacing between individual airfoil sections

        Repeater {
            model: airfoilModel

            delegate: Item {
                width: parent.width
                // Dynamically adjust height based on the children's combined height
                height: childrenRect.height
                // Header for each airfoil section (collapsible part)
                // Header for each airfoil section (collapsible part)
                Rectangle {
                    id: header
                    width: parent.width
                    height: 50
                    color: "#4CAF50" // Green header color
                    border.color: "#388E3C" // Darker green border
                    border.width: 1
                    radius: 8 // Rounded corners for a modern look
                    // Add a subtle drop shadow for depth
                    //                    layer.enabled: true
                    //                    layer.effect: DropShadow {
                    //                        color: "#80000000" // Semi-transparent black
                    //                        radius: 4
                    //                        samples: 8
                    //                        horizontalOffset: 2
                    //                        verticalOffset: 2
                    //                    }

                    Text {
                        text: name // Display the airfoil name from the model
                        anchors.verticalCenter: parent.verticalCenter
                        left: parent.left + 15
                        font.bold: true
                        font.pixelSize: 18
                        color: "white" // White text for contrast
                    }

                    // Collapse/Expand indicator (arrow icon)
                    //                    Image {
                    //                        id: arrowIcon
                    //                        // Source changes based on the 'collapsed' state from the model
                    //                        source: model.collapsed ? "qrc:///qtquickcontrols2/material/icons/arrow_drop_down.svg" : "qrc:///qtquickcontrols2/material/icons/arrow_drop_up.svg"
                    //                        width: 24
                    //                        height: 24
                    //                        anchors.verticalCenter: parent.verticalCenter
                    //                        right: parent.right - 15 // Position on the right
                    //                        fillMode: Image.PreserveAspectFit // Maintain aspect ratio
                    //                        //                            color: "white" // Tint the SVG icon white
                    //                    }

                    // MouseArea to make the header clickable
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            // Call setData on the Python model to toggle the 'collapsed' state
                            // model.index refers to the current item's index in the Repeater's model
                            airfoilModel.setData(model.index, !model.collapsed, "collapsed")
                        }
                    }
                }

                // Collapsible content area for actions
                Item {
                    id: contentArea
                    width: parent.width
                    y: header.height + 5 // Position slightly below the header
//                    spacing: 5
                    // Visibility is bound to the 'collapsed' state from the model
                    visible: !model.collapsed
                    // Opacity for smooth fade-in/fade-out effect
                    opacity: visible ? 1 : 0

                    // Behaviors for smooth animation during collapse/expand
                    Behavior on opacity {
                        NumberAnimation { duration: 200 }
                    }
                    Behavior on height {
                        NumberAnimation { duration: 200 }
                    }

                    // ListView to display the actions for the current airfoil
                    ListView {
                        id: actionsListView
                        width: parent.width
                        // Auto-adjust height based on the content of its delegates
                        height: contentHeight
                        clip: true // Clip content that goes beyond the ListView's bounds
                        // The model for this ListView is the 'actions' list from the current airfoil item
                        model: actions

                        delegate: Rectangle {
                            width: parent.width
                            height: 40 // Fixed height for each action item for consistency
                            color: "white" // White background for action items
                            border.color: "#e0e0e0" // Light grey border
                            border.width: 1
                            radius: 4 // Rounded corners
//                            padding: 10 // Internal padding for text

                            Text {
                                // For a simple list of strings, 'model.display' holds the string value
                                text: model.display
                                anchors.verticalCenter: parent.verticalCenter
                                left: parent.left + 10
                                font.pixelSize: 16
                                color: "#333333" // Dark grey text color
                            }
                        }
                    }
                }
            }
        }
    }
}

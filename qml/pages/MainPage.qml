import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtCharts 2.12
import QtQuick.Dialogs 1.2
import "../components"

Item {
    implicitHeight: 625
    implicitWidth: 880
    id: content_page
    property int spacing: 6

    Rectangle {
        id: addContainer
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.right: transformContainer.left
        radius: 10
        anchors.margins: 10
        color: "#e3e3e3"
        border.color: "#33334c"
        //        width: 320
        height: 80

        Label {
            text: "Add airfoil"
            font.pointSize: 6
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 5
            anchors.top: parent.top
        }

        RowLayout {
            anchors.topMargin: 15
            anchors.rightMargin: content_page.spacing
            anchors.leftMargin: content_page.spacing
            anchors.top:parent.top
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            spacing: 8


            CustomComboBox {
                id: select_foilCombobox
                Layout.fillWidth: true
                Layout.minimumWidth: 120
                Layout.minimumHeight: 40

                onCurrentValueChanged: {
                    dataModel.load(select_foilCombobox.currentValue)
                    console.log(select_foilCombobox.currentValue)
                }
            }
            TextButton {
                id: openButton
                text: qsTr("Open")
//                Layout.minimumWidth: 60
                Layout.minimumHeight: 40
                colorDefault: "white"
            }
            TextButton {
                id: duplicateButton
                text: qsTr("Duplicate")
//                Layout.fillWidth: true
                Layout.minimumHeight: 40
//                Layout.minimumWidth: 80

                colorDefault: "white"
            }
        }
    }
    Rectangle {
        id: transformContainer
        //        anchors.left: addContainer.right
        anchors.top: parent.top
        anchors.right: parent.right
        radius: 10
        anchors.margins: 10
        color: "#e3e3e3"
        border.color: "#33334c"
        width: 0.5 * parent.width
        height: 80

        Label {
            text: "Transform"
            font.pointSize: 6
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 5
            anchors.top: parent.top
        }

        RowLayout {
            anchors.topMargin: 15
            anchors.rightMargin: content_page.spacing
            anchors.leftMargin: content_page.spacing
            anchors.top:parent.top
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            spacing: 8

            TextButton {
                id: translateButton
                text: qsTr("Translate")
                Layout.fillWidth: true
//                Layout.minimumWidth: 80
                Layout.minimumHeight: 40
                colorDefault: "white"
                onClicked: {
                    translateDialog.open()
                }
            }
            TextButton {
                id: scaleButton
                height: 30
                text: qsTr("Scale")
                Layout.fillWidth: true
                Layout.minimumWidth: 50
                Layout.minimumHeight: 40
                colorDefault: "white"
            }
            TextButton {
                id: rotateButton
                width: 60
                height: 30
                text: qsTr("Rotate")
                Layout.fillWidth: true
                Layout.minimumWidth: 60
                Layout.minimumHeight: 40
                colorDefault: "white"
            }
            TextButton {
                id: flipButton
                height: 30
                text: qsTr("Flip")
                Layout.fillWidth: true
                Layout.minimumWidth: 50
                Layout.minimumHeight: 40
                colorDefault: "white"
            }

            Popup {
                id: translateDialog
                width: 200
                height: 200
                visible: false

                background: Rectangle {
                    id: translateDialog_bg
                    implicitWidth: parent.width
                    implicitHeight: parent.height
                    border.color: "#707070"
                    border.width: 1
                    radius: 10
                }
                contentItem: Item {
                    width: parent.width - 10
                    height: parent.height - 10
                    anchors.centerIn: translateDialog_bg
                    ManipulationSpinBox {
                        id: xSpinbox
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 10
                    }
                    ManipulationSpinBox {
                        id: ySpinbox
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: xSpinbox.bottom
                        anchors.margins: 10
                    }
                }
            }
        }
    }

    ListView {
        id: actionList
        width: 150
        height: 50

        anchors.top: addContainer.bottom
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 10
//        spacing: 5

        delegate: actionDelegate
        model: actionlistModel

        section.delegate: action_sectionDelegate
        section.property: "airfoil"

        Rectangle {
            id: actionlistBg
            color: "#e3e3e3"
            radius: 5
            z: -1
            border.color: "#707070"
            border.width: 2
            anchors.fill: parent
        }

        Component {
            id: action_sectionDelegate
            Item {
                id: rectangle

                width: actionList.width - 5 // actionList.childrenRect.width //actionList.contentItem.width
                height: sectiontext.height + 15

                Rectangle {
                    id: action_child
                    anchors.fill: parent
                    anchors.margins: 5
                    color: "lightsteelblue"
                    border.width: 2
                    radius: 5
                    border.color: "#5094ee"
//                    Rectangle {
//                        width: 2
//                        //height: actionList.section.
//                        //height: actionList.contentHeight
//                    }
                }
                Label {
                    id: sectiontext
                    text: section
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 10
                    font.bold: true
                }
            }
        }
        ListModel {
            id: actionlistModel
            ListElement {
                actionName: "load";
                airfoil: "NACA 2212"
            }
            ListElement {
                actionName: "rotate";
                airfoil: "NACA 2212"
            }
            ListElement {
                actionName: "translate";
                airfoil: "NACA 2212"
            }
            ListElement {
                actionName: "scale";
                airfoil: "NACA 2212"
            }
            ListElement {
                actionName: "load";
                airfoil: "NACA 2208"
            }
            ListElement {
                actionName: "scale";
                airfoil: "NACA 2208"
            }
        }

        Component {
            id: actionDelegate
            Rectangle {
                x: 10
                width: 5
                height: childrenRect.height //+ 2
                color: "black"
                border.width: 2
//                radius: border.width

                Label {
                    text: actionName
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    horizontalAlignment: Text.AlignHCenter
                    font.pointSize: 12
                }
            }
        }
    }

    //    ManipulationSpinBox {
    //        id: rotationSpinbox
    //        unit: "deg"
    //        anchors.left: parent.left
    //        anchors.right: parent.right
    //        anchors.top: select_foil_combobox.bottom
    //        anchors.margins: 10
    //    }
    //    ManipulationSpinBox {
    //        id: scalingSpinbox
    //        anchors.left: parent.left
    //        anchors.right: parent.right
    //        anchors.top: rotationSpinbox.bottom
    //        anchors.margins: 10
    //    }
    //

    TextButton {
        // eliminate button by assigning its function to onCurrentItemCHanged of the combobox
        // and set the initial item of the combobox to empty, with the text "select foil"
        // add to python backend to do nothing if the function is called on an empty path, instead of crash on an error
        text: "Clear"
        anchors.bottom: parent.bottom
        anchors.margins: 15
        anchors.right: parent.right
        height: 30
        width: 50
        onClicked: {
            foil_chart.removeAllSeries() // clear the chart
            select_foil_combobox.currentIndex = 0 //reset the combobox to empty state
        }
    }

    ChartView {
        id: foil_chart
        anchors.top: addContainer.bottom
        anchors.left: actionList.right
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        plotAreaColor: "#000020"
        backgroundColor: "white"
        legend.visible: false
        antialiasing: true
        //        axes: [myaxisX, myaxisY]
        //        setAxisX: myaxisX
        //        setAxisY: myaxisY

        function loadChartData() {
            foil_chart.clearChart()

            var series = foil_chart.createSeries(LineSeries, "Data Plot", myaxisX, myaxisY);
            for (var i = 0; i < dataModel.data.length; ++i) {
                console.log(i);
                //console.log(dataModel.data[i][0], dataModel.data[i][1]);
                series.append(dataModel.data[i][0], dataModel.data[i][1]);
            }
        }
        function clearChart() {
            foil_chart.removeAllSeries()
        }

        Connections {
            target: dataModel
            // update this name to the new
            // update the signal, such that the new data is raised with the signal
            function onDataChanged () {
                console.log('data changed')
                //console.log(dataModel.data)
                foil_chart.loadChartData();
            }
        }
        //width: 600
        //plotArea: Qt.rect(5, 5, foil_chart.width - 5, foil_chart.height - 5)
        //margins { top: 10; bottom: 10; left: 10; right: 10; }

        ValueAxis {
            id:myaxisX
            min: -0.2; max: 1.2
            tickCount: 11
        }
        ValueAxis {
            id:myaxisY
            min: -0.5; max: 0.5
            tickCount: 11
        }
    }
}

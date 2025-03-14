import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import "../components"

Item {
    //height: 625
    //width: 880
    id: content_page

    Rectangle {
        id: control_container
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 5
        radius: 10
        color: "transparent"
        border.color: "#33334c"
        width: 200

        CustomComboBox {
            id: select_foil_combobox
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 10
            //width: 100
            height: 50
            //x: 20
            //y: 30
            textRole: "text"
            valueRole: "path"
            model: ListModel {
                id: foilItems
                ListElement {
                    text: "Select airfoil"
                    path: ""
                }

                ListElement {
                    // populate this model with a script that reads
                    // the contents of the directory and creates a model
                    text: "clark-y"
                    path: "../../airfoils/naca02115.dat"
                }
            }
            onCurrentValueChanged: {
                dataModel.loadData(select_foil_combobox.currentValue)
                //onCurrentIndexChanged: console.debug(cbItems.get(currentIndex).text + ", " + cbItems.get(currentIndex).color)
            }
        }
        ManipulationSpinBox {
            id: rotationSpinbox
            unit: "deg"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: select_foil_combobox.bottom
            anchors.margins: 10
        }
        ManipulationSpinBox {
            id: scalingSpinbox
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: rotationSpinbox.bottom
            anchors.margins: 10
        }
        ManipulationSpinBox {
            id: xSpinbox
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: scalingSpinbox.bottom
            anchors.margins: 10
        }
        ManipulationSpinBox {
            id: ySpinbox
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: xSpinbox.bottom
            anchors.margins: 10
        }

        CustomButton {
            // eliminate button by assigning its function to onCuurentItemCHanged of the combobox
            // and set the initial item of the combobox to empty, with the text "select foil"
            // add to python backend to do nothing if the function is called on an empty path, instead of crash on an error
            text: "Clear"
            anchors.bottom: parent.bottom
            anchors.margins: 10
            anchors.right: parent.right
            height: 30
            width: 50
            onClicked: {
                foil_chart.removeAllSeries() // clear the chart
                select_foil_combobox.currentIndex = 0 //reset the combobox to empty state
            }
        }
    }

    ChartView {
        id: foil_chart
        anchors.top: parent.top
        anchors.left: control_container.right
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        plotAreaColor: "#000020"
        backgroundColor: "white"
        legend.visible: false
        antialiasing: true

        function loadChartData() {
            foil_chart.removeAllSeries()

            var series = foil_chart.createSeries(LineSeries, "Data Plot", myaxisX, myaxisY);
            for (var i = 0; i < dataModel.data.length; ++i) {
                series.append(dataModel.data[i].x, dataModel.data[i].y);
                //console.log(i);
                //console.log(dataModel.data[i][0], dataModel.data[i][1]);
                //series.append(dataModel.data[i][0], dataModel.data[i][1]);

            }
        }

        Connections {
            target: dataModel
            onDataChanged: {
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
            min: 0; max: 1
            tickCount: 11
        }
        ValueAxis {
            id:myaxisY
            min: -0.5; max: 0.5
            tickCount: 11
        }
    }
}

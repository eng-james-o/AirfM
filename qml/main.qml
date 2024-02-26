import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import "components"

Window {
    width: 900
    height: 720
    minimumWidth: 800
    minimumHeight: 650
    visible: true
    color: "#00000000"
    id: mainWindow
    title: qsTr("AirfM")

    // Remove title bar
    flags: Qt.Window | Qt.FramelessWindowHint

    // Text Edit Properties
    //property alias actualPage: stackView.currentItem
    property bool isValueVisible: true
    property int windowStatus: 0
    property int windowMargin: 10
    property int bgRadius: 20

    // Internal functions
    QtObject{
        id: internal

        function resetResizeBorders(){
            // Resize visibility
            resizeLeft.visible = true
            resizeRight.visible = true
            resizeBottom.visible = true
            resizeApp.visible = true
            bg.radius = bgRadius
            bg.border.width = 3
        }

        function maximizeRestore(){
            if(windowStatus == 0){
                mainWindow.showMaximized()
                windowStatus = 1
                windowMargin = 0
                // Resize visibility
                resizeLeft.visible = false
                resizeRight.visible = false
                resizeBottom.visible = false
                resizeApp.visible = false
                bg.radius = 0
                bg.border.width = 0
                btnMaximizeRestore.btnIconSource = "../images/svg_images/restore_icon.svg"
            }
            else{
                mainWindow.showNormal()
                windowStatus = 0
                windowMargin = 10
                // Resize visibility
                internal.resetResizeBorders()
                bg.border.width = 3
                btnMaximizeRestore.btnIconSource = "../images/svg_images/maximize_icon.svg"
            }
        }

        function ifMaximizedWindowRestore(){
            if(windowStatus == 1){
                mainWindow.showNormal()
                windowStatus = 0
                windowMargin = 10
                // Resize visibility
                internal.resetResizeBorders()
                bg.border.width = 3
                btnMaximizeRestore.btnIconSource = "../images/svg_images/maximize_icon.svg"
            }
        }

        function restoreMargins(){
            windowStatus = 0
            windowMargin = 10
            bg.radius = bgRadius
            // Resize visibility
            internal.resetResizeBorders()
            bg.border.width = 3
            btnMaximizeRestore.btnIconSource = "../images/svg_images/maximize_icon.svg"
        }
    }

    Rectangle {
        id: frame
        //opacity: 0
        color: "#1d1d2b"
        radius: 20
        border.color: "#33334c"
        border.width: 3
        anchors.fill: parent
        anchors.margins: windowMargin
        clip: true
        z: 1

        AppBar {
            id: topBar
            anchors.top: frame.top
            anchors.left: frame.left
            anchors.right: frame.right
            anchors.margins: 5
            appBarRadius: 15
        }

        MouseArea {
            id: resizeLeft
            width: 12
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 15
            anchors.leftMargin: 0
            anchors.topMargin: 10
            cursorShape: Qt.SizeHorCursor
            DragHandler{
                target: null
                onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.LeftEdge) }
            }
        }

        MouseArea {
            id: resizeRight
            width: 12
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.rightMargin: 0
            anchors.bottomMargin: 25
            anchors.leftMargin: 6
            anchors.topMargin: 10
            cursorShape: Qt.SizeHorCursor
            DragHandler{
                target: null
                onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.RightEdge) }
            }
        }

        MouseArea {
            id: resizeBottom
            height: 12
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            cursorShape: Qt.SizeVerCursor
            anchors.rightMargin: 25
            anchors.leftMargin: 15
            anchors.bottomMargin: 0
            DragHandler{
                target: null
                onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.BottomEdge) }
            }
        }

        MouseArea {
            id: resizeApp
            x: 1176
            y: 697
            width: 25
            height: 25
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.rightMargin: 0
            cursorShape: Qt.SizeFDiagCursor
            DragHandler{
                target: null
                onActiveChanged: if (active){
                                     mainWindow.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
                                 }
            }
        }
        Rectangle {
            anchors.top: topBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            radius: parent.radius
            color: "transparent"

            ComboBox {
                id: select_foil_combobox
                width: 100
                height: 60
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                textRole: "text"
                valueRole: "path"
                model: ListModel {
                    ListElement {
                        // populate this model with a script that checks the contents of the directory
                        text: "clark-y"
                        path: "C:/Users/PC/Documents/Research and Projects/James-Mary AC design/airfoils/clarky.dat"
                    }
                }
            }

            Button {
                text: "Load data"
                anchors.left: select_foil_combobox.right
                anchors.verticalCenter: select_foil_combobox.verticalCenter
                height: 60

                onClicked: {
                    dataModel.loadData(select_foil_combobox.currentValue)
                    //foil_chart.update()
                }
            }
            ChartView {
                id: foil_chart
                anchors.top: select_foil_combobox.bottom
                height: 200
                width: 300
                plotArea: Qt.rect(5, 5, foil_chart.width - 5, foil_chart.height - 5)
                margins { top: 10; bottom: 10; left: 10; right: 10; }

                plotAreaColor: "#000020"
                backgroundColor: "white"
                legend.visible: false
                antialiasing: true

                LineSeries {
                    id: line_series
                    name: "data plot"
                    axisX: axisX
                    axisY: axisY
                    /*XYPoint {
                        x:0; y:0
                    }
                    XYPoint {
                        x:0.2; y:0.3
                    }
                    XYPoint {
                        x:0.4; y:0.4
                    }
                    XYPoint {
                        x:0.6; y:0.3
                    }
                    XYPoint {
                        x:0.8; y:0.15
                    }
                    XYPoint {
                        x:1.0; y:0
                    }*/
                    Repeater {
                        model: dataModel.getData()
                        LineSeries {
                            XYPoint {
                                x: model.x; y:model.y
                            }
                        }
                    }
                }
                ValueAxis {
                    id:axisX
                    min: 0; max: 1
                    tickCount: 11
                }
                ValueAxis {
                    id:axisY
                    min: 0; max: 1
                    tickCount: 11
                }
            }
        }
    }
}

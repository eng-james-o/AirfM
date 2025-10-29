import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

ComboBox {
    id: control
    //property var customModel: []
    currentIndex: -1

    model: airfoilListModel ? airfoilListModel : null
    textRole: "name"
    valueRole: "path"
    implicitWidth: 120
    implicitHeight: 40

    //    onCurrentTextChanged: {console.log("CustomComboBox: ", control.model.name)}
    //    onCurrentValueChanged: {console.log("CustomComboBox: ", control.model.name)}

    delegate: ItemDelegate {
        width: control.width
        contentItem: Text {
            text: model.name
            color: "#49906a"
            font: control.font
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            border.color: "#212bbe"
            color: control.highlighted? "#899889":"#328242"
            radius: 2
        }

        highlighted: control.highlightedIndex === index
    }

    indicator: Canvas {
        id: canvas
        x: control.width - width - control.rightPadding
        y: control.topPadding + (control.availableHeight - height) / 2
        width: 12
        height: 8
        contextType: "2d"

        Connections {
            target: control
            function onPressedChanged() { canvas.requestPaint(); }
        }

        onPaint: {
            context.reset();
            context.moveTo(0, 0);
            context.lineTo(width, 0);
            context.lineTo(width / 2, height);
            context.closePath();
            context.fillStyle = control.pressed ? "#17a81a" : "#21be2b";
            context.fill();
        }
    }

    contentItem: Text {
        id: comboDisplayText
        leftPadding: 10
        rightPadding: control.indicator.width + control.spacing

        text: control.currentIndex < 0? "Select Airfoil" : control.displayText
        font: control.font
        color: control.pressed ? "#17a81a" : "#21be2b"
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: control.width //120
        implicitHeight: control.height // 40
        border.color: control.pressed ? "#17a81a" : "#21be2b"
        border.width: control.visualFocus ? 2 : 1
        radius: 5

    }

    popup: Popup {
        y: control.height - 1
        width: control.width
        implicitHeight: contentItem.implicitHeight
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator { }
        }

        background: Rectangle {
            border.color: "#21be2b"
            //color: "#546484"
            //radius: 2
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/

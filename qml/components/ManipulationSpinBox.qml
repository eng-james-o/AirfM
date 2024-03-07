import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SpinBox {
    id: control
    property int decimals: 2
    property real realValue: value / 100
    property string unit: ""
    property var suffix: unit==""? "" : "\xB0"

    from: -360
    value: 0
    to: 360
    stepSize: 1
    editable: true

    validator: DoubleValidator {
        bottom: Math.min(control.from, control.to)
        top:  Math.max(control.from, control.to)
    }

    textFromValue: function(value, locale) {
        //return Number(value / 100).toLocaleString(locale, 'f', control.decimals) // to move the value by 0.01
        return Number(value).toLocaleString(locale, 'f', control.decimals)
    }

    valueFromText: function(text, locale) {
        //return Number.fromLocaleString(locale, text) * 100 // to move the value by 0.01
        return Number.fromLocaleString(locale, text)
    }

    contentItem: TextInput {
        z: 2
        text: control.textFromValue(control.value, control.locale) + suffix

        font: control.font
        color: "#21be2b"
        selectionColor: "#21be2b"
        selectedTextColor: "#ffffff"
        horizontalAlignment: Qt.AlignHCenter
        verticalAlignment: Qt.AlignVCenter

        readOnly: !control.editable
        validator: control.validator
        //inputMethodHints: Qt.ImhFormattedNumbersOnly
    }

    up.indicator: Rectangle {
        x: control.mirrored ? 0 : parent.width - width
        height: parent.height
        implicitWidth: 40
        implicitHeight: 40
        color: control.up.pressed ? "#e4e4e4" : "#f6f6f6"
        border.color: enabled ? "#21be2b" : "#bdbebf"

        Text {
            text: "+"
            font.pixelSize: control.font.pixelSize * 2
            color: "#21be2b"
            anchors.fill: parent
            fontSizeMode: Text.Fit
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    down.indicator: Rectangle {
        x: control.mirrored ? parent.width - width : 0
        height: parent.height
        implicitWidth: 40
        implicitHeight: 40
        color: control.down.pressed ? "#e4e4e4" : "#f6f6f6"
        border.color: enabled ? "#21be2b" : "#bdbebf"

        Text {
            text: "-"
            font.pixelSize: control.font.pixelSize * 2
            color: "#21be2b"
            anchors.fill: parent
            fontSizeMode: Text.Fit
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    background: Rectangle {
        implicitWidth: 140
        border.color: "#bdbebf"
    }
}

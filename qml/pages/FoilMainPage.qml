import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtCharts 2.12
import QtQuick.Dialogs 1.2
import "../components"

Item {
    TabBar {
        id: tabBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        onCurrentIndexChanged: {
            swipeView.currentIndex = currentIndex
        }
            TabButton {
            text: "2D Foil"
        }
        TabButton {
            text: "3D Foil"
        }
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        currentIndex: tabBar.currentIndex
        onCurrentIndexChanged: {
            tabBar.currentIndex = currentIndex
        }
        Foil2DPage {
            id: foil2DPage
            anchors.fill: parent
        }
        Foil3DPage {
            id: foil3DPage
            anchors.fill: parent
        }
    }
}
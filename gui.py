from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json

from themes import *
from messages import *

class Gui(QMainWindow):
    def __init__(self, loop, app, **kwargs):
        super(__class__, self).__init__(**kwargs)
        self.host = ()
        self.app = app
        self.loop = loop
        self.friends = self.app.friends
        self.color = self.app.color
        self.theme = self.app.theme

    def initialize(self):
        self.widget = uic.loadUi(self.theme["ui_path"] + "/Main.ui", self)
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)
        self.setWindowTitle('Pesterchum')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.appLabel.mousePressEvent = self.label_mousePressEvent
        self.appLabel.mouseMoveEvent = self.label_mouseMoveEvent
        self.nameButton.setText(self.app.nick)
        self.tabWindow = None
        
        self.menubar = self.menuBar()
        self.clientMenu = self.menubar.addMenu("Client")
        self.profileMenu = self.menubar.addMenu("Profile")
        self.helpMenu = self.menubar.addMenu("Help")

        self.exitClient = QAction("Exit",self)
        self.exitClient.triggered.connect(self.app.exit)
        self.clientMenu.addAction(self.exitClient)

        self.mood_buttons = dict(chummy=self.chummyButton,
                                 bully=self.bullyButton,
                                 palsy=self.palsyButton,
                                 chipper=self.chipperButton,
                                 peppy=self.peppyButton,
                                 rancorous=self.rancorousButton,
                                 abscond=self.abscondButton)
        self.nameButton.setIcon(QIcon(self.theme["path"] + "/chummy.png"))
        for name, button in self.mood_buttons.items():
            button.setIcon(QIcon(os.path.join(self.theme["path"], name + ".png")))
            button.setStyleSheet(self.theme["styles"])
            button.clicked.connect(self.make_setMood(button))

        self.colorButton.clicked.connect(self.color_picker)

        for item in self.friends.keys():
            treeitem = QTreeWidgetItem()
            treeitem.setText(0, item)
            treeitem.setIcon(0, QIcon(self.theme["path"] + "/offline.png"))
            self.chumsTree.addTopLevelItem(treeitem)
            
        self.chumsTree.itemDoubleClicked.connect(self.open_privmsg)
        self.pesterButton.clicked.connect(self.privmsg_pester)
        
        self.colorButton.setStyleSheet('background-color:' + self.color)
        self.show()

    def start_privmsg(self, user):
        if not self.tabWindow:
            self.tabWindow = TabWindow(self, user)
            return self.tabWindow.init_user
        else:
            return self.tabWindow.add_user(user)

    @pyqtSlot(QTreeWidgetItem)
    def open_privmsg(self, item):
        user = item.text(0)
        self.start_privmsg(user)

    def privmsg_pester(self):
        selected = self.chumsTree.selectedItems()
        if selected:
            user = selected[0].text(0)
            self.start_privmsg(user)

    def color_picker(self):
        color = QColorDialog.getColor()
        self.color = color.name()
        self.colorButton.setStyleSheet('background-color:' + self.color + ';')
        self.app.change_color(self.color)

    def make_setMood(self, button):
        def setMood():
            for name, moodButton in self.mood_buttons.items():
                if button != moodButton:
                    moodButton.setChecked(False)
                else:
                    self.nameButton.setIcon(QIcon(os.path.join(self.theme["path"], name + ".png")))
        return setMood

    @pyqtSlot()
    def label_mousePressEvent(self, event):
        self.offset = event.pos()

    @pyqtSlot()
    def label_mouseMoveEvent(self, event):
        x=event.globalX()
        y=event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
        
class PrivateMessageWidget(QWidget):
    def __init__(self, container, parent, user):
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(self.parent.parent.theme["ui_path"] + "/PrivateMessageWidget.ui", self)
        self.user = user
        self.userLabel.setText(user.join("::"))
        self.userOutput.setEnabled(False)
        self.sendButton.clicked.connect(self.send)
        
    def send(self):
        msg = self.userInput.text()
        if msg:
            user = self.user
            self.parent.parent.app.send_msg(msg, user=user)
            self.userInput.setText("")
            self.display_text(msg)          

    def display_text(self, msg, user=None):
        try:
            nmsg = fmt_disp_msg(self.parent.parent.app, msg, user=user)
            self.userOutput.insertHtml(nmsg)
        except Exception as e:
            print(e)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.send()

class TabWindow(QWidget):
    def __init__(self, parent, user):
        super(__class__, self).__init__()
        self.parent=parent
        uic.loadUi(parent.theme["ui_path"] + "/TabWindow.ui", self)
        self.users = []
        self.init_user = self.add_user(user)
        self.tabWidget.removeTab(0)
        self.tabWidget.removeTab(0)
        self.setWindowTitle("Private Message")
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.closeEvent(self.closeEvent)
        self.show()

    def closeEvent(self, event):
        self.parent.tabWindow = None
        self.destroy()
        
    def add_user(self, user):
        if not user in self.users:
            windw = PrivateMessageWidget(self.tabWidget, self, user)
            a = self.tabWidget.addTab(windw, user)
            tab = self.tabWidget.widget(a)
            tab.setStyleSheet(self.parent.theme["styles"])
            self.users.append(user)
            return tab
        else:
            return self.tabWidget.widget(self.users.index(user))

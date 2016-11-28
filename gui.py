from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json

from themes import *
from messages import *
from dialogs import *

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
        self.clientMenu.setStyleSheet(self.theme["styles"])
        self.profileMenu = self.menubar.addMenu("Profile")
        self.helpMenu = self.menubar.addMenu("Help")

        self.exitClient = QAction("EXIT",self)
        self.exitClient.triggered.connect(self.app.exit)
        self.clientMenu.addAction(self.exitClient)

        self.openSwitch = QAction("SWITCH", self)
        self.openSwitch.triggered.connect(self.openSwitchDialog)
        self.profileMenu.addAction(self.openSwitch)

        self.mood_buttons = {self.chummyButton.text():self.chummyButton,
                                 self.prankyButton.text():self.prankyButton,
                                 self.pleasantButton.text():self.pleasantButton,
                                 self.smoothButton.text():self.smoothButton,
                                 self.distraughtButton.text():self.distraughtButton,
                                 self.rancorousButton.text():self.rancorousButton,
                                 self.abscondButton.text():self.abscondButton}
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
        
        self.addChumButton.clicked.connect(self.openFriendDialog)
        
        self.colorButton.setStyleSheet('background-color:' + self.color)
        self.show()

    def openSwitchDialog(self):
        self.switchDialog = SwitchDialog(self.app, self)

    def openFriendDialog(self):
        self.friendDialog = AddFriendDialog(self.app, self)

    def start_privmsg(self, user):
        try:
            self.app.send_begin(user)
            if not self.tabWindow:
                self.tabWindow = TabWindow(self.app, self, user)
                return self.tabWindow.init_user
            else:
                return self.tabWindow.add_user(user)
        except Exception as e:
            print(e)

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
        self.app.change_color(self.color)

    def make_setMood(self, button):
        def setMood():
            try:
                for name, moodButton in self.mood_buttons.items():
                    if button != moodButton:
                        moodButton.setChecked(False)
                    else:
                        self.nameButton.setIcon(QIcon(os.path.join(self.theme["path"], name + ".png")))
                        self.app.changeMood(name)
            except Exception as e:
                print(e)
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
        

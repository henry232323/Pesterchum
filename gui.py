from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json
import asyncio
from asyncio import async as aioasync

from themes import *
from messages import *
from dialogs import *
from ui_initialization import *

class Gui(QMainWindow):
    def __init__(self, loop, app, **kwargs):
        super(__class__, self).__init__(**kwargs)
        self.host = ()
        self.app = app
        self.loop = loop
        self.friends = self.app.friends
        self.color = self.app.color
        self.theme = self.app.theme
        #Set current PM window and Connecting to none
        self.tabWindow = None
        self.connectingDialog = None

    def initialize(self):
        '''Initialize GUI creation'''
        self.widget = uic.loadUi(self.theme["ui_path"] + "/Main.ui", self)
        #Fix dimensions
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)
        
        #Set window info
        self.setWindowTitle('Pesterchum')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)

        #Initialize Menu
        initialize_menu(self)
        #Initialize Buttons
        initialize_buttons(self)

        #Create a QTreeWidgetItem for each friend and add it to the chumsTree dropdown
        #Assume by default they are offline
        for item in self.friends.keys():
            treeitem = QTreeWidgetItem()
            treeitem.setText(0, item)
            treeitem.setIcon(0, QIcon(self.theme["path"] + "/offline.png"))
            self.chumsTree.addTopLevelItem(treeitem)

        self.chumsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chumsTree.customContextMenuRequested.connect(self.openChumsMenu)

        #Open new private message on doubleclick
        self.chumsTree.itemDoubleClicked.connect(self.open_privmsg)
        self.pesterButton.clicked.connect(self.privmsg_pester)
        self.blockButton.clicked.connect(self.block_selected)

        #Open Add Friend dialog
        self.addChumButton.clicked.connect(self.openFriendDialog)

        #Set background of Color button to current color
        self.colorButton.setStyleSheet('background-color:' + self.color)
        
        self.show()

    def openSwitchDialog(self):
        self.switchDialog = SwitchDialog(self.app, self)

    def openFriendDialog(self):
        self.friendDialog = AddFriendDialog(self.app, self)

    def openBlockedDialog(self):
        self.blockedDialog = BlockedDialog(self.app, self)

    def openChumsMenu(self, position):
        indexes = self.chumsTree.selectedIndexes()
        if indexes:
            menu = QMenu()
            menu.addAction(self.removeFriendContext)
            menu.exec_(self.chumsTree.viewport().mapToGlobal(position))

    def openUserList(self):
        self.userList = UserlistWindow(self.app, self)

    def openOptions(self):
        self.userList = OptionsWindow(self.app, self)

    async def openReconnect(self):
        self.connectingDialog = ConnectingDialog(self.app, self)

    async def closeReconnect(self):
        if self.connectingDialog:
            self.connectingDialog.close()
            self.connectingDialog = None

    def remove_chum(self):
        items = self.chumsTree.selectedItems()
        if items:
            user = items[0].text(0)
            item = items[0]
            self.app.remove_friend(user, item=item)
            
    def start_privmsg(self, user):
        '''
        Start a private message window, if one exists add a user to it
        Return the new tab of the user
        '''
        if not self.tabWindow:
            self.tabWindow = TabWindow(self.app, self, user)
            return self.tabWindow.init_user
        else:
            return self.tabWindow.add_user(user)

    @pyqtSlot(QTreeWidgetItem)
    def open_privmsg(self, item):
        user = item.text(0)
        self.start_privmsg(user)
        self.tabWindow.raise_()
        self.tabWindow.activateWindow()

    @pyqtSlot(QListWidgetItem)
    def open_privmsg_userlist(self, item):
        user = item.text()
        self.start_privmsg(user)
        self.tabWindow.raise_()
        self.tabWindow.activateWindow()

    def privmsg_pester(self):
        '''Opens selected user in tree when PESTER! button pressed, same as double click'''
        selected = self.chumsTree.selectedItems()
        if selected:
            user = selected[0].text(0)
            self.start_privmsg(user)
            self.tabWindow.raise_()
            self.tabWindow.activateWindow()

    def block_selected(self):
        '''Blocks the currently selected user in chumsTree'''
        selected = self.chumsTree.selectedItems()
        if selected:
            user = selected[0].text(0)
            if user in self.app.friends.keys():
                if user not in self.app.blocked:
                    index = self.app.gui.chumsTree.indexOfTopLevelItem(self.app.gui.getFriendItem(user)[0])
                    self.app.gui.chumsTree.takeTopLevelItem(index)
            self.app.add_blocked(user)
    def color_picker(self):
        '''Open color picker dialog, change current user color and change colorButton background'''
        color = QColorDialog.getColor()
        self.color = color.name()
        self.app.change_color(self.color)

    def make_setMood(self, button):
        '''Makes set mood button for each button, each button deselects all others and sets user mood'''
        def setMood():
            for name, moodButton in self.mood_buttons.items():
                if button == moodButton:
                    self.nameButton.setIcon(QIcon(os.path.join(self.theme["path"], name + ".png")))
                    self.app.changeMood(name)
                else:
                    moodButton.setChecked(False)
        return setMood

    def getFriendItem(self, name):
        '''Get the tree item in the chumsTree from a name'''
        item = self.chumsTree.findItems(name, Qt.MatchContains, 0)
        return item

    #Methods for moving window
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
        

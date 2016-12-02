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

        #Make window movable from 'Pesterchum' label, for lack of Title Bar
        self.appLabel.mousePressEvent = self.label_mousePressEvent
        self.appLabel.mouseMoveEvent = self.label_mouseMoveEvent
        self.nameButton.setText(self.app.nick)

        #Set current PM window to none
        self.tabWindow = None

        #Initialize top Menu
        self.menubar = self.menuBar()
        self.clientMenu = self.menubar.addMenu("Client")
        self.clientMenu.setStyleSheet(self.theme["styles"])
        self.profileMenu = self.menubar.addMenu("Profile")
        self.helpMenu = self.menubar.addMenu("Help")

        #Create EXIT button in 'CLIENT' menu
        self.exitClient = QAction("EXIT",self)
        self.exitClient.triggered.connect(self.app.exit)
        self.clientMenu.addAction(self.exitClient)

        #Create SWITCH button in 'PROFILE' menu
        self.openSwitch = QAction("SWITCH", self)
        self.openSwitch.triggered.connect(self.openSwitchDialog)
        self.profileMenu.addAction(self.openSwitch)

        #Create COLOR button in 'PROFILE' menu
        self.openPicker = QAction("COLOR", self)
        self.openPicker.triggered.connect(self.color_picker)
        self.profileMenu.addAction(self.openPicker)

        #Create TROLLSLUM button in 'PROFILE' menu
        self.openTrollslum = QAction("TROLLSLUM", self)
        self.openTrollslum.triggered.connect(self.openBlockedDialog)
        self.profileMenu.addAction(self.openTrollslum)

        #Make dictionary of all current mood buttons, manual for now
        self.mood_buttons = {self.chummyButton.text():self.chummyButton,
                                 self.prankyButton.text():self.prankyButton,
                                 self.pleasantButton.text():self.pleasantButton,
                                 self.smoothButton.text():self.smoothButton,
                                 self.distraughtButton.text():self.distraughtButton,
                                 self.rancorousButton.text():self.rancorousButton,
                                 self.abscondButton.text():self.abscondButton}
        self.nameButton.setIcon(QIcon(self.theme["path"] + "/chummy.png"))
        #Set stylesheet and set an action for every defined mood button
        #In the dictionary, give it the corresponding Icon
        for name, button in self.mood_buttons.items():
            button.setIcon(QIcon(os.path.join(self.theme["path"], name + ".png")))
            button.setStyleSheet(self.theme["styles"])
            button.clicked.connect(self.make_setMood(button))

        #Make color picker open on opening of the Color Button
        self.colorButton.clicked.connect(self.color_picker)

        #Create a QTreeWidgetItem for each friend and add it to the chumsTree dropdown
        #Assume by default they are offline
        for item in self.friends.keys():
            treeitem = QTreeWidgetItem()
            treeitem.setText(0, item)
            treeitem.setIcon(0, QIcon(self.theme["path"] + "/offline.png"))
            self.chumsTree.addTopLevelItem(treeitem)

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
            self.app.add_blocked(user)
            self.chumsTree.removeItem(selected[0])

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
        

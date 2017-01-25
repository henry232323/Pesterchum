from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QDesktopServices, \
     QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSlot, QUrl, QModelIndex, QVariant
from PyQt5 import uic

import os.path, json
import asyncio

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
        self.memoTabWindow = None
        self.memosWindow = None

    def initialize(self):
        '''Initialize GUI creation'''
        self.widget = uic.loadUi(self.theme["ui_path"] + "/Main.ui", self)
        #Fix dimensions
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)

        #Make window movable from 'Pesterchum' label, for lack of Title Bar
        self.appLabel.mousePressEvent = self.label_mousePressEvent
        self.appLabel.mouseMoveEvent = self.label_mouseMoveEvent
        
        #Set window info
        self.setWindowTitle('Pesterchum')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)

        #Initialize Menu
        initialize_menu(self)
        #Initialize Buttons
        initialize_buttons(self)

        #Create QStandardItemModel for QTreeView
        self.friendsModel = self.FriendsModel(self.app)
        self.friendsItems = dict()
        #Create a QStandardItem for each friend, friendsModel will auto update
        #Assume by default they are offline
        for friend in self.friends.keys():
            treeitem = QStandardItem(friend)
            treeitem.setText(friend)
            treeitem.setIcon(QIcon(self.theme["path"] + "/offline.png"))
            self.friendsModel.appendRow(treeitem)
            self.friendsItems[friend] = treeitem

        self.drawTree()
        self.friendsModel.sort(0)
        self.chumsTree.setModel(self.friendsModel)
        self.chumsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chumsTree.customContextMenuRequested.connect(self.openChumsMenu)
        self.chumsTree.setSelectionMode(QTreeView.SingleSelection)
        self.chumsTree.setSelectionBehavior(QTreeView.SelectRows)
        self.chumsTree.setExpandsOnDoubleClick(True)
        self.chumsTree.setItemsExpandable(True)

        #Open new private message on doubleclick
        self.chumsTree.doubleClicked.connect(self.open_privmsg)
        self.pesterButton.clicked.connect(self.privmsg_pester)
        self.blockButton.clicked.connect(self.block_selected)

        #Open Add Friend dialog
        self.addChumButton.clicked.connect(self.openFriendDialog)

        #Set background of Color button to current color
        self.colorButton.setStyleSheet('background-color:' + self.color)
        
        #Name Button
        self.nameButton.setText(self.app.nick)
        self.nameButton.clicked.connect(self.openSwitchDialog)
        
        self.show()

    #def closeEvent(self, event):
    #    event.accept()
    #    self.app.exit()

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
            menu.addAction(self.blockContext)
            menu.exec_(self.chumsTree.viewport().mapToGlobal(position))

    def openUserList(self):
        self.userList = UserlistWindow(self.app, self)

    def openOptions(self):
        self.optionsWindow = OptionsWindow(self.app, self)

    def openMemosWindow(self):
        self.memosWindow = MemosWindow(self.app, self)

    def openCalspritePM(self):
        self.start_privmsg("calSprite")

    def openNickservPM(self):
        self.start_privmsg("nickServ")

    def openHelp(self):
        QDesktopServices.openUrl(QUrl("https://github.com/henry232323/Pesterchum"))

    def openBug(self):
        QDesktopServices.openUrl(QUrl("https://github.com/henry232323/Pesterchum/issues"))
        
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

    @pyqtSlot(QModelIndex)
    def open_privmsg(self, itemindex):
        user = self.friendsModel.data(itemindex)
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
        selected = self.chumsTree.selectedIndexes()
        if selected:
            idx = selected[0]
            user = self.friendsModel.data(idx)
            self.start_privmsg(user)
            self.tabWindow.raise_()
            self.tabWindow.activateWindow()

    def block_selected(self):
        '''Blocks the currently selected user in chumsTree'''
        selected = self.chumsTree.selectedIndexes()
        if selected:
            idx = selected[0]
            user = self.friendsModel.data(idx)
            if user in self.app.friends.keys():
                if user not in self.app.blocked:
                    self.app.gui.friendsModel.removeRow(idx.row())
            self.app.add_blocked(user)
            
    def color_picker(self):
        '''Open color picker dialog, change current user color and change colorButton background'''
        color = QColorDialog.getColor()
        self.color = color.name()
        self.app.change_color(self.color)

    def make_setMood(self, button):
        '''Makes set mood button for each button, each button deselects all others and sets user mood'''
        def setMood():
            if not button.isChecked():
                button.setChecked(True)
                return
            for num, moodButton in self.mood_buttons.items():
                if button == moodButton:
                    mood_name = self.app.moods.getName(num)
                    self.nameButton.setIcon(QIcon(os.path.join(self.theme["path"], mood_name + ".png")))
                    self.app.changeMood(mood_name)
                else:
                    moodButton.setChecked(False)
        return setMood

    def getFriendItem(self, name):
        '''Get the tree item in the chumsTree from a name'''
        return self.friendsItems[name]

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

    def drawTree(self):
        if self.app.options["chum_list"]["hide_offline_chums"]:
            for name, item in self.friendsItems.items():
                if name not in self.app.online:
                    index = self.friendsModel.indexFromItem(item)
                    a = self.chumsTree.setRowHidden(index.row(),self.friendsModel.parent(index), True)
        else:
            for name, item in self.friendsItems.items():
                if name not in self.app.online:
                    index = self.friendsModel.indexFromItem(item)
                    self.chumsTree.setRowHidden(index.row(),self.friendsModel.parent(index), False)
            
    
    class FriendsModel(QStandardItemModel):
        def __init__(self, app, parent=None):
            QStandardItemModel.__init__(self, parent)
            self.app = app
            self.header_labels = ["Chums ({}/{})".format(len(self.app.online), len(self.app.friends))]
            
        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if self.app.options["chum_list"]["show_number_of_online_chums"]:
                fmt = "Chums"
            else:
                fmt = "Chums ({}/{})"
            self.header_labels = [fmt.format(len(self.app.online), len(self.app.friends))]
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                return self.header_labels[section]
            return QStandardItemModel.headerData(self, section, orientation, role)

        def update(self):
            a = self.setHeaderData(0, Qt.Orientation(1),
                               QVariant("Chums ({}/{})".format(len(self.app.online), len(self.app.friends))))

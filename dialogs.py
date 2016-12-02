from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json

from themes import *
from messages import *

class PrivateMessageWidget(QWidget):
    def __init__(self, app, container, parent, user):
        '''
        The widget within each tab of TabWindow, a display
        for new private messages and user input
        '''
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(self.parent.parent.theme["ui_path"] + "/PrivateMessageWidget.ui", self)
        self.user = user
        self.app = app
        self.userLabel.setText(user.join(["::", "::"]))
        self.userOutput.setEnabled(False)
        self.sendButton.clicked.connect(self.send)
        self.display_text(fmt_begin_msg(app, self.app.nick, user))
        
    def send(self):
        '''Send the user the message in the userInput box, called on enter press / send button press'''
        msg = self.userInput.text()
        if msg:
            user = self.user
            self.app.send_msg(msg, user=user)
            self.userInput.setText("")
            fmt = fmt_disp_msg(self.app, msg, user=self.app.nick)
            self.display_text(fmt)

    def display_text(self, msg):
        '''Insert msg into the display box'''
        self.userOutput.insertHtml(msg)

    def keyPressEvent(self, event):
        '''Use enter key to send'''
        if event.key() == Qt.Key_Return:
            self.send()

class TabWindow(QWidget):
    def __init__(self, app, parent, user):
        '''
        A window for storing PrivateMessageWidget instances, a navigation
        between current private message users
        '''
        super(__class__, self).__init__()
        self.parent=parent
        self.app = app
        uic.loadUi(parent.theme["ui_path"] + "/TabWindow.ui", self)
        self.users = []
        self.init_user = self.add_user(user)
        self.tabWidget.removeTab(0)#Remove two default tabs
        self.tabWidget.removeTab(0)
        self.setWindowTitle("Private Message")
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.show()

    def closeEvent(self, event):
        '''On window (or tab) close send a PESTERCHUM:CEASE message to each user, destroy self'''
        self.app.tabWindow = None
        for user in self.users:
            self.app.send_cease(user)
        self.destroy()
        
    def add_user(self, user):
        '''
        Add a user & PrivateMessageWidget to window, check if it is already there
        if so, return that user's PM, if not, create and return a PM
        On PrivateMessageWidget creation, send a PESTERCHUM:BEGIN initiation message
        '''
        if not user in self.users:
            windw = PrivateMessageWidget(self.app, self.tabWidget, self, user)
            self.app.send_begin(user)
            a = self.tabWidget.addTab(windw, user)
            tab = self.tabWidget.widget(a)
            tab.setStyleSheet(self.app.theme["styles"])
            self.users.append(user)
            return tab
        else:
            return self.tabWidget.widget(self.users.index(user))

class SwitchDialog(QDialog):
    def __init__(self, app, parent):
        '''
        A blocking dialog appearing when the user Switch dialog is opened
        Located in the 'Profile' menu
        '''
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(parent.theme["ui_path"] + "/SwitchDialog.ui", self)
        self.app = app
        self.setWindowTitle('Switch')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.setStyleSheet(self.parent.theme["styles"])
        self.proceedButton.clicked.connect(self.accepted)
        self.cancelButton.clicked.connect(self.close)
        self.deleteProfileButton.clicked.connect(self.delete_profile)
        self.colorButton.clicked.connect(self.color_picker)
        self.colorButton.setStyleSheet('background-color:' + self.app.color)
        self.color = self.parent.color
        self.profilesDropdown.insertItem(0, "Choose a profile...")
        self.profilesDropdown.insertItems(1, self.app.users.keys())
        self.changeFromLabel.setText("CHANGING FROM {}".format(self.app.nick))
        self.show()

    def color_picker(self):
        '''Open Color Picker dialog, set user's color and colorButton background'''
        color = QColorDialog.getColor()
        self.color = color.name()
        self.colorButton.setStyleSheet('background-color:' + self.color + ';')

    def accepted(self):
        '''Called on accept, changes Nick'''
        nick = self.getHandleInput.text()
        selected_name = self.profilesDropdown.currentText()
        if nick:
            self.app.change_nick(nick, self.color)
        elif selected_name != "Choose a profile...":
            self.app.change_nick(selected_name, self.app.users[selected_name])
        self.close()

    def delete_profile(self):
        '''
        Called when attempting to delete profile, asks for confirmation
        Removes name from selectable profiles and users list
        '''
        selected_name = self.profilesDropdown.currentText()
        confirm = ConfirmDeleteDialog(self.app, self, selected_name)
        if confirm.accepted:
            if selected_name in self.app.users.keys():
                del self.app.users[selected_name]
                self.profilesDropdown.removeItem(self.profilesDropdown.currentIndex())

class ConfirmDeleteDialog(QDialog):
    def __init__(self, app, parent, user):
        '''
        Dialog opened when attempting to delete a profile
        in the switch menu
        '''
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(self.app.theme["ui_path"] + "/ConfirmDeleteDialog.ui", self)
        self.setWindowTitle('Confirm Delete')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.acceptButton.clicked.connect(self.accepted)
        self.rejectButton.clicked.connect(self.rejected)
        self.confirmLabel.setText("Are you sure you want to delete profile {}".format(user))
        self.exec_()

    def accepted(self):
        self.accepted = True
        self.close()

    def rejected(self):
        self.accepted = False
        self.close()

class AddFriendDialog(QDialog):
    def __init__(self, app, parent):
        '''
        Dialog opened when the Add [Chum] button is pressed, adds to chumsTree widget
        '''
        super(__class__, self).__init__()
        self.parent = parent
        self.app = app
        uic.loadUi(self.app.theme["ui_path"] + "/AddFriendDialog.ui", self)
        self.setWindowTitle('Add Chum')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.acceptButton.clicked.connect(self.accepted)
        self.rejectButton.clicked.connect(self.close)
        self.exec_()
        
    def accepted(self):
        '''Call once accepted, check if name is alphanumeric if not warn and try again'''
        user = self.addChumInput.text()
        if user and user.isalpha():
            self.app.add_friend(user)
            self.close()
        else:
            try:
                self.err = InvalidUserDialog(self.app, self, user)
            except Exception as e:
                print(e)
                
class AddBlockedDialog(QDialog):
    def __init__(self, app, parent):
        '''
        Dialog opened when the Add button is pressed in TROLLSLUM, adds to parent.blockedList widget
        '''
        super(__class__, self).__init__()
        self.parent = parent
        self.app = app
        uic.loadUi(self.app.theme["ui_path"] + "/AddBlockedDialog.ui", self)
        self.setWindowTitle('TROLLSLUM')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.acceptButton.clicked.connect(self.accepted)
        self.rejectButton.clicked.connect(self.close)
        self.exec_()

    def accepted(self):
        '''Call once accepted, check if name is alphanumeric if not warn and try again'''
        user = self.addChumInput.text()
        if user and (user not in self.app.blocked):
            self.app.add_blocked(user)
            item = QListWidgetItem(user)
            self.parent.blockedList.addItem(item)
            if user in self.app.friends.keys():
                index = self.app.gui.chumsTree.indexOfTopLevelItem(self.app.gui.getFriendItem(user)[0])
                self.app.gui.chumsTree.takeTopLevelItem(index)

            self.close()
        else:
            self.close()

class InvalidUserDialog(QDialog):
    def __init__(self, app, parent, user):
        '''
        Opened when attempting to add a friend with an invalid username
        Right now only called if the name is non-alphanumeric
        Only warns
        '''
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/InvalidUserDialog.ui", self)
        self.setWindowTitle('Invalid Name')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        fmt = "Name <span style='font_weight: bold;'>{}</style> is not valid! Make sure it is alphanumeric"
        self.errUserLabel.setText(fmt.format(user))                                  
        self.acceptButton.clicked.connect(self.close)
        self.exec_()
        
class BlockedDialog(QDialog):
    def __init__(self, app, parent):
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/BlockedDialog.ui", self)
        self.app = app
        self.parent = parent
        self.setWindowTitle('TROLLSLUM')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.addBlockButton.clicked.connect(self.add)
        self.removeBlockButton.clicked.connect(self.remove)
        for user in self.app.blocked:
            self.blockedList.addItem(QListWidgetItem(user))
        self.exec_()

    def add(self):
        dialog = AddBlockedDialog(self.app, self)

    def remove(self):
        try:
            selected = self.blockedList.selectedItems()
            if selected:
                item = selected[0]
                index = self.blockedList.indexFromItem(item)
                self.blockedList.takeItem(index.row())
                user = item.text()
                self.app.blocked.remove(user)
                if user in self.app.friends.keys():
                    treeitem = QTreeWidgetItem()
                    treeitem.setText(0, user)
                    treeitem.setIcon(0, QIcon(self.app.theme["path"] + "/offline.png"))
                    self.app.gui.chumsTree.addTopLevelItem(treeitem)
        except Exception as e:
            print(e)

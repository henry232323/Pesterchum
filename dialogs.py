from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json

from themes import *
from messages import *

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
            fmt = fmt_disp_msg(self.parent.parent.app, msg, user=self.parent.parent.app.nick)
            self.display_text(fmt)

    def display_text(self, msg):
        self.userOutput.insertHtml(msg)

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
        self.show()

    def closeEvent(self, event):
        self.parent.tabWindow = None
        for user in self.users:
            self.parent.app.send_cease(user)
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

class SwitchDialog(QDialog):
    def __init__(self, parent):
        super(__class__, self).__init__()
        try:
            self.parent = parent
            uic.loadUi(parent.theme["ui_path"] + "/SwitchDialog.ui", self)
            self.setWindowTitle('Switch')
            self.setWindowIcon(QIcon("resources/pc_chummy.png"))
            self.setStyleSheet(self.parent.theme["styles"])
            self.palette().highlight().setColor(QColor("#CCC"))
            self.proceedButton.clicked.connect(self.accepted)
            self.cancelButton.clicked.connect(self.close)
            self.deleteProfileButton.clicked.connect(self.delete_profile)
            self.colorButton.clicked.connect(self.color_picker)
            self.colorButton.setStyleSheet('background-color:' + self.parent.color)
            self.color = self.parent.color
            self.profilesDropdown.insertItem(0, "Choose a profile...")
            self.profilesDropdown.insertItems(1, self.parent.app.users.keys())
            self.changeFromLabel.setText("CHANGING FROM {}".format(self.parent.app.nick))
            self.show()
        except Exception as e:
            print(e)

    def color_picker(self):
        color = QColorDialog.getColor()
        self.color = color.name()
        self.colorButton.setStyleSheet('background-color:' + self.color + ';')

    def accepted(self):
        nick = self.getHandleInput.text()
        selected_name = self.profilesDropdown.currentText()
        if nick:
            self.parent.app.change_nick(nick, self.color)
        elif selected_name != "Choose a profile...":
            self.parent.app.change_nick(selected_name, self.parent.app.users[selected_name])
        self.close()

    def delete_profile(self):
        selected_name = self.profilesDropdown.currentText()
        confirm = ConfirmDeleteDialog(self, selected_name)
        if confirm.accepted:
            if selected_name in self.parent.app.users.keys():
                del self.parent.app.users[selected_name]
                self.profilesDropdown.removeItem(self.profilesDropdown.currentIndex())

class ConfirmDeleteDialog(QDialog):
    def __init__(self, parent, user):
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(self.parent.parent.theme["ui_path"] + "/ConfirmDeleteDialog.ui", self)
        self.setWindowTitle('Confirm Delete')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.confirmButtonBox.accepted.connect(self.accepted)
        self.confirmButtonBox.rejected.connect(self.rejected)
        self.confirmButtonBox.clicked.connect(self.close)
        self.confirmLabel.setText("Are you sure you want to delete profile {}".format(user))
        self.exec_()

    def accepted(self):
        self.accepted = True

    def rejected(self):
        self.accepted = False

class AddFriendDialog(QDialog):
    def __init__(self, parent):
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(self.parent.theme["ui_path"] + "/AddFriendDialog.ui", self)
        self.setWindowTitle('Add Chum')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.confirmButtonBox.accepted.connect(self.accepted)
        self.confirmButtonBox.clicked.connect(self.close)
        self.exec_()

    def accepted(self):
        user = self.addChumInput.text()
        if user and user.isalpha():
            self.parent.app.add_friend(user)

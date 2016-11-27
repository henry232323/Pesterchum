from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
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
        self.clientMenu.setStyleSheet(self.theme["styles"])
        self.profileMenu = self.menubar.addMenu("Profile")
        self.helpMenu = self.menubar.addMenu("Help")

        self.exitClient = QAction("EXIT",self)
        self.exitClient.triggered.connect(self.app.exit)
        self.clientMenu.addAction(self.exitClient)

        self.openSwitch = QAction("SWITCH", self)
        self.openSwitch.triggered.connect(self.openSwitchDialog)
        self.profileMenu.addAction(self.openSwitch)

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

    def openSwitchDialog(self):
        self.switchDialog = SwitchDialog(self)

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
        self.confirmButtonBox.accepted.connect(self.accepted)
        self.confirmButtonBox.rejected.connect(self.rejected)
        self.confirmLabel.setText("Are you sure you want to delete profile {}".format(user))
        self.exec_()

    def accepted(self):
        self.accepted = True
        self.close()

    def rejected(self):
        self.accepted = False
        self.close()

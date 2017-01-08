from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QTextCursor, QStandardItem, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json, sys

from themes import *
from messages import *
from formatting import fmt_memo_msg, rgb

class PrivateMessageWidget(QWidget):
    def __init__(self, app, container, parent, user):
        '''
        The widget within each tab of TabWindow, a display
        for new private messages and user input
        '''
        super(__class__, self).__init__()
        self.parent = parent
        uic.loadUi(app.theme["ui_path"] + "/PrivateMessageWidget.ui", self)
        self.user = user
        self.app = app
        self.userLabel.setText(user.join(["::", "::"]))
        self.sendButton.clicked.connect(self.send)
        self.userOutput.setReadOnly(True)
        self.userOutput.setMouseTracking(True)
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
        cursor = self.userOutput.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.userOutput.setTextCursor(cursor)
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
        uic.loadUi(app.theme["ui_path"] + "/TabWindow.ui", self)
        self.users = []
        self.init_user = self.add_user(user)
        self.tabWidget.removeTab(0)#Remove two default tabs
        self.tabWidget.removeTab(0)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setWindowTitle("Private Message")
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.show()

    def closeTab(self, currentIndex):
        widget = self.tabWidget.widget(currentIndex)
        widget.deleteLater()
        self.tabWidget.removeTab(currentIndex)
        if widget.user != "nickServ":
            self.app.send_cease(widget.user)
        self.users.remove(widget.user)
        if not self.users:
            self.close()

    def closeEvent(self, event):
        '''On window (or tab) close send a PESTERCHUM:CEASE message to each user, destroy self'''
        for user in self.users:
            if user != "nickServ":
                self.app.send_cease(user)
        event.accept()
        self.app.gui.tabWindow = None
        
    def add_user(self, user):
        '''
        Add a user & PrivateMessageWidget to window, check if it is already there
        if so, return that user's PM, if not, create and return a PM
        On PrivateMessageWidget creation, send a PESTERCHUM:BEGIN initiation message
        '''
        if not user in self.users:
            windw = PrivateMessageWidget(self.app, self.tabWidget, self, user)
            if user != "nickServ":
                self.app.send_begin(user)
            icon = QIcon("resources/pc_chummy.png")
            a = self.tabWidget.addTab(windw, icon, user)
            tab = self.tabWidget.widget(a)
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
        uic.loadUi(app.theme["ui_path"] + "/SwitchDialog.ui", self)
        self.app = app
        self.setWindowTitle('Switch')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
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
            self.err = InvalidUserDialog(self.app, self, user)
                
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
        selected = self.blockedList.selectedItems()
        if selected:
            item = selected[0]
            index = self.blockedList.indexFromItem(item)
            self.blockedList.takeItem(index.row())
            user = item.text()
            self.app.blocked.remove(user)
            if user in self.app.friends.keys():
                treeitem = QStandardItem(user)
                treeitem.setText(user)
                treeitem.setIcon(QIcon(self.app.theme["path"] + "/offline.png"))
                self.app.gui.friendsModel.appendRow(treeitem)

class ConnectingDialog(QDialog):
    def __init__(self, app, parent):
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/ConnectingDialog.ui", self)
        self.app = app
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.connectingExitButton.clicked.connect(sys.exit)
        self.setWindowTitle('Connecting')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.app.gui.connectingDialog = self
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)

        self.exec_()

class UserlistWindow(QWidget):
    def __init__(self, app, parent):
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/UserlistWindow.ui", self)
        self.app = app
        self.parent = parent
        self.closeUserlist.clicked.connect(self.close)
        self.setWindowTitle('Userlist')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))

        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)

        self.userList.setSortingEnabled(True)
        self.userList.addItems(self.app.names_list["#pesterchum"])
        self.userList.itemDoubleClicked.connect(self.app.gui.open_privmsg_userlist)
    
        self.show()

class OptionsWindow(QWidget):
    def __init__(self, app, parent):
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/OptionsWindow.ui", self)    
        self.app = app
        self.parent = parent
        self.setWindowTitle('Options')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        self.options = self.app.options
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)
        self.buttons = (self.optionsButton1,self.optionsButton2,self.optionsButton3,self.optionsButton4,
                        self.optionsButton5,self.optionsButton6,self.optionsButton7,self.optionsButton8)

        for index, button in enumerate(self.buttons):
            button.clicked.connect(self.make_call(index, button))
            
        self.acceptButton.clicked.connect(self.saveConfig)
        self.rejectButton.clicked.connect(self.close)
        self.themesComboBox.addItems(self.app.themes.keys())
        self.themesComboBox.setInsertPolicy(QComboBox.InsertAlphabetically)
        index = self.themesComboBox.findText(self.app.theme_name)
        self.themesComboBox.setCurrentIndex(index)
        self.refreshThemeButton.clicked.connect(lambda: self.app.change_theme(self.app.theme_name))

        convo_opt = self.options["conversations"]
        chum_opt = self.options["chum_list"]
        interface_opt = self.options["interface"]
        
        #Chum List
        self.hideOfflineRadio.setChecked(chum_opt["hide_offline_chums"])
        self.showEmptyRadio.setChecked(chum_opt["show_empty_groups"])
        self.showNumberRadio.setChecked(chum_opt["show_number_of_online_chums"])
        self.sortChumsCombo.addItems(("Alphabetically", "Mood"))
        self.sortChumsCombo.setCurrentIndex(chum_opt["sort_chums"])
        self.lowBandwidthRadio.setChecked(chum_opt["low_bandwidth"])
        #Conversations
        self.timeStampsRadio.setChecked(convo_opt["time_stamps"])
        self.showSecondsRadio.setChecked(convo_opt["show_seconds"])
        self.opVoiceMemoRadio.setChecked(convo_opt["op_and_voice_in_memos"])
        self.animatedSmiliesRadio.setChecked(convo_opt["use_animated_smilies"])
        self.randomEncountersRadio.setChecked(convo_opt["receive_random_encounters"])
        self.clockTypeComboBox.addItems(('12','24'))
        self.clockTypeComboBox.setCurrentIndex(convo_opt["clock_type"])
        #Interface
        self.tabbedConvoBox.setChecked(interface_opt["tabbed_conversations"])
        self.tabbedMemoBox.setChecked(interface_opt["tabbed_memos"])
        self.blinkPesterBox.setChecked(interface_opt["blink_taskbar_on_pesters"])
        self.blinkMemoBox.setChecked(interface_opt["blink_taskbar_on_memos"])
        self.minimizeCombo.addItems(('Minimize to Taskbar','Minimize to Tray', 'Quit'))
        self.minimizeCombo.setCurrentIndex(interface_opt["minimize"])
        self.closeCombo.addItems(('Minimize to Taskbar','Minimize to Tray', 'Quit'))
        self.closeCombo.setCurrentIndex(interface_opt["close"])
    
        self.show()
        
    def saveConfig(self):
        oldtheme = self.app.theme_name
        try:
            #Chum List
            self.options["chum_list"]["hide_offline_chums"] = self.hideOfflineRadio.isChecked()
            self.options["chum_list"]["show_empty_groups"] = self.showEmptyRadio.isChecked()
            self.options["chum_list"]["show_number_of_online_chums"] = self.showNumberRadio.isChecked()
            self.options["chum_list"]["sort_chums"] = self.sortChumsCombo.currentIndex()
            self.options["chum_list"]["low_bandwidth"] = self.lowBandwidthRadio.isChecked()
            #Conversations
            self.options["conversations"]["time_stamps"] = self.timeStampsRadio.isChecked()
            self.options["conversations"]["show_seconds"] = self.showSecondsRadio.isChecked()
            self.options["conversations"]["op_and_voice_in_memos"] = self.opVoiceMemoRadio.isChecked()
            self.options["conversations"]["use_animated_smilies"] = self.animatedSmiliesRadio.isChecked()
            self.options["conversations"]["receive_random_encounters"] = self.randomEncountersRadio.isChecked()
            self.options["conversations"]["clock_type"] = self.clockTypeComboBox.currentIndex()
            #Interface
            self.options["interface"]["tabbed_conversations"] = self.tabbedConvoBox.isChecked()
            self.options["interface"]["tabbed_memos"] = self.tabbedMemoBox.isChecked()
            self.options["interface"]["blink_taskbar_on_pesters"] = self.blinkPesterBox.isChecked()
            self.options["interface"]["blink_taskbar_on_memos"] = self.blinkMemoBox.isChecked()
            self.options["interface"]["minimize"] = self.minimizeCombo.currentIndex()
            self.options["interface"]["close"] = self.closeCombo.currentIndex()

            self.app.options_changed()
            self.app.change_theme(self.themesComboBox.currentText())
        except Exception as e:
            self.errorLabel.setText("Error changing theme: \n{}".format(e))
            self.app_change_theme(oldtheme)
        self.close()

    def make_call(self, index, button):
        def setIndex():
            self.stackedWidget.setCurrentIndex(index)
            button.setChecked(True)
            for Button in self.buttons:
                if button != Button:
                    Button.setChecked(False)
                
        return setIndex

class MemosWindow(QWidget):
    def __init__(self, app, parent):
        super(__class__, self).__init__()
        uic.loadUi(app.theme["ui_path"] + "/MemoWindow.ui", self)    
        self.app = app
        self.parent = parent
        self.setWindowTitle('Memos')
        self.setWindowIcon(QIcon("resources/pc_chummy.png"))
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setFixedSize(width, height)
        self.memosTableWidget.setColumnCount(2)
        self.memosTableWidget.setHorizontalHeaderLabels(["Memo", "Users"])
        self.memosTableWidget.doubleClicked.connect(self.openMemo)
        header = self.memosTableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.ctr = 0
        self.app.send_list()

        self.show()

    def openMemo(self, index):
        channel = self.memosTableWidget.itemFromIndex(index).text()
        if not self.app.gui.memoTabWindow:
            self.app.gui.memoTabWindow = MemoTabWindow(self.app, self, channel)
            self.close()
            return self.app.gui.memoTabWindow.init_memo
        else:
            self.close()
            return self.app.gui.memoTabWindow.add_memo(channel)

    def add_channel(self, memo, usercount):
        self.memosTableWidget.insertRow(self.ctr)
        icn = QIcon(self.app.theme["path"] + "/memo.png")
        mitem = QTableWidgetItem(icn,memo)
        mitem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable) | Qt.ItemFlags(Qt.ItemIsEnabled))
        uitem = QTableWidgetItem()
        uitem.setData(0,usercount)
        uitem.setTextAlignment(2)
        uitem.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable) | Qt.ItemFlags(Qt.ItemIsEnabled))
        self.memosTableWidget.setItem(self.ctr,0,mitem)
        self.memosTableWidget.setItem(self.ctr,1,uitem)
        self.ctr += 1

    def closeEvent(self, event):
        event.accept()
        self.app.gui.memosWindow = None

class MemoMessageWidget(QWidget):
    def __init__(self, app, container, parent, memo):
        '''
        The widget within each tab of TabWindow, a display
        for new private messages and user input
        '''
        super(__class__, self).__init__()
        self.parent = parent
        self.names = []
        uic.loadUi(app.theme["ui_path"] + "/MemoMessageWidget.ui", self)
        self.memo = memo
        self.app = app
        self.times = dict()
        self.time = 'i'
        self.names = set()
        self.userLabel.setText(memo.join(["::", "::"]))
        self.sendButton.clicked.connect(self.send)
        self.userOutput.setReadOnly(True)
        self.userOutput.setMouseTracking(True)
        self.app.join(channel=memo)
        self.app.send_msg("PESTERCHUM:TIME>i", user=memo)
        
    def send(self):
        '''Send the user the message in the userInput box, called on enter press / send button press'''
        msg = self.userInput.text()
        if msg:
            memo = self.memo
            sendmsg = fmt_memo_msg(self.app, msg, self.app.nick)
            disp = fmt_disp_memo(self.app, sendmsg, user=self.app.nick)
            self.app.send_msg(sendmsg, user=memo)
            self.userInput.setText("")
            self.display_text(disp)
            
    def add_names(self, names):
        self.names = set(names)
        names = list(set(self.names))
        for user in names:
            self.add_user_item(user)

    def add_user_item(self, user):
        if user.startswith("@"):
            nam = user[1:]
            self.memoUsers.addItem(nam)
            itm = self.memoUsers.item(self.memoUsers.count()-1)
            itm.setIcon(QIcon(self.app.theme["path"] + "/op.png"))
        elif user.startswith("&"):
            nam = user[1:]
            self.memoUsers.addItem(nam)
            itm = self.memoUsers.item(self.memoUsers.count()-1)
            itm.setIcon(QIcon(self.app.theme["path"] + "/admin.png"))
        elif user.startswith("%"):
            nam = user[1:]
            self.memoUsers.addItem(nam)
            itm = self.memoUsers.item(self.memoUsers.count()-1)
            itm.setIcon(QIcon(self.app.theme["path"] + "/halfop.png"))                
        else:
            nam = user
            self.memoUsers.addItem(nam)
            itm = self.memoUsers.item(self.memoUsers.count()-1)
        color = self.app.getColor(nam)
        if color.startswith("rgb"):
            r,g,b = color.split(",")
            r = int(r[-2:])
            g = int(g)
            b = int(b[:-1])
        else:
            r,g,b = rgb(color, type=tuple)
        itm.setForeground(QColor(r,g,b))

    def display_text(self, msg):
        '''Insert msg into the display box'''
        cursor = self.userOutput.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.userOutput.setTextCursor(cursor)
        self.userOutput.insertHtml(msg)

    def keyPressEvent(self, event):
        '''Use enter key to send'''
        if event.key() == Qt.Key_Return:
            self.send()

    def user_join(self, user):
        if user not in self.names:
            itm = self.memoUsers.addItem(user)
            self.send_time()
            self.add_user_item(user)
            self.names.add(user)

        time = self.times[user] if user in self.times.keys() else "i"
        join_msg = fmt_memo_join(self.app, user, time, self.memo, opened=True)
        self.display_text(join_msg)

    def user_part(self, user):
        item = self.memoUsers.findItems(user, Qt.MatchFlags(Qt.MatchExactly))
        row = self.memoUsers.row(item[0])
        self.memoUsers.takeItem(row)
        
        time = self.times[user] if user in self.times.keys() else "i"
        part_msg = fmt_memo_join(self.app, user, time, self.memo, part=True)
        self.display_text(part_msg)

    def send_time(self, time='i'):
        self.app.send_msg("PESTERCHUM:TIME>{}".format(time), user=self.memo)

class MemoTabWindow(QWidget):
    def __init__(self, app, parent, memo):
        '''
        A window for storing PrivateMessageWidget instances, a navigation
        between current private message users
        '''
        super(__class__, self).__init__()
        self.parent=parent
        self.app = app
        uic.loadUi(app.theme["ui_path"] + "/MemoTabWindow.ui", self)
        self.memos = []
        self.init_memo = self.add_memo(memo)
        self.tabWidget.removeTab(0)#Remove two default tabs
        self.tabWidget.removeTab(0)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setWindowTitle("Memos")
        self.setWindowIcon(QIcon(self.app.theme["path"] + "/memo.png"))
        self.app.gui.memoTabWindow = self
        self.show()

    def closeTab(self, currentIndex):
        widget = self.tabWidget.widget(currentIndex)
        widget.deleteLater()
        self.tabWidget.removeTab(currentIndex)
        self.memos.remove(widget.memo)
        self.app.part(channel=widget.memo)
        if not self.memos:
            self.close()

    def closeEvent(self, event):
        '''On window (or tab) close send a PESTERCHUM:CEASE message to each user, destroy self'''
        for memo in self.memos:
            self.app.part(channel=memo)
        event.accept()
        self.app.gui.memoTabWindow = None

    def add_names(self, memo, names):
        if memo in self.memos:
            tab = self.getWidget(memo)
            tab.add_names(names)

    def getWidget(self, memo):
        if memo in self.memos:
            return self.tabWidget.widget(self.memos.index(memo))
        else:
            return None
            
    def add_memo(self, memo):
        '''
        Add a user & PrivateMessageWidget to window, check if it is already there
        if so, return that user's PM, if not, create and return a PM
        On PrivateMessageWidget creation, send a PESTERCHUM:BEGIN initiation message
        '''
        if not memo in self.memos:
            windw = MemoMessageWidget(self.app, self.tabWidget, self, memo)
            icon = QIcon(self.app.theme["path"] + "/memo.png")
            a = self.tabWidget.addTab(windw, icon, memo)
            tab = self.tabWidget.widget(a)
            self.memos.append(memo)
            return tab
        else:
            return self.getWidget(memo)

#!/usr/bin/python3
# Copyright (c) 2016-2017, henry232323
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor, QDesktopServices
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5 import uic

import os.path, json
import asyncio

def initialize_menu(self):
    #Initialize top Menu
    self.menubar = self.menuBar()
    self.clientMenu = self.menubar.addMenu("CLIENT")
    self.profileMenu = self.menubar.addMenu("PROFILE")
    self.helpMenu = self.menubar.addMenu("HELP")

    #Create OPTIONS button in 'CLIENT' menu
    self.optionsAction = QAction("OPTIONS",self)
    self.optionsAction.triggered.connect(self.openOptions)
    self.clientMenu.addAction(self.optionsAction)

    #Create MEMOS button in 'CLIENT' menu
    self.openMemos = QAction("MEMOS",self)
    self.openMemos.triggered.connect(self.openMemosWindow)
    self.clientMenu.addAction(self.openMemos)

    #Create USERLIST button in 'CLIENT' menu
    self.userlistAction = QAction("USERLIST",self)
    self.userlistAction.triggered.connect(self.openUserList)
    self.clientMenu.addAction(self.userlistAction)

    #Create IDLE button in 'CLIENT' menu
    self.idleAction = QAction("IDLE", self)
    self.idleAction.setCheckable(True)
    self.idleAction.toggled.connect(self.app.toggle_idle)
    self.clientMenu.addAction(self.idleAction)

    #Create RECONNECT button in 'CLIENT' menu
    self.reconnectClient = QAction("RECONNECT",self)
    self.reconnectClient.triggered.connect(self.app.reconnect)
    self.clientMenu.addAction(self.reconnectClient)

    #Create EXIT button in 'CLIENT' menu
    self.exitClient = QAction("EXIT",self)
    self.exitClient.triggered.connect(self.app.exit)
    self.clientMenu.addAction(self.exitClient)

    #Create TROLLSLUM button in 'PROFILE' menu
    self.openTrollslum = QAction("TROLLSLUM", self)
    self.openTrollslum.triggered.connect(self.openBlockedDialog)
    self.profileMenu.addAction(self.openTrollslum)

    #Create COLOR button in 'PROFILE' menu
    self.openPicker = QAction("COLOR", self)
    self.openPicker.triggered.connect(self.color_picker)
    self.profileMenu.addAction(self.openPicker)

    self.quirkAction = QAction("QUIRKS", self)


    # Create QUIRKS button in 'PROFILE' menu
    self.quirkAction = QAction("QUIRKS", self)
    self.quirkAction.triggered.connect(self.openQuirkWindow)
    self.profileMenu.addAction(self.quirkAction)

    #Create SWITCH button in 'PROFILE' menu
    self.openSwitch = QAction("SWITCH", self)
    self.openSwitch.triggered.connect(self.openSwitchDialog)
    self.profileMenu.addAction(self.openSwitch)

    #Create HELP button in 'HELP' menu
    self.openHelpAction = QAction("HELP", self)
    self.openHelpAction.triggered.connect(self.openHelp)
    self.helpMenu.addAction(self.openHelpAction)

    #Create NICKSERV button in 'HELP' menu
    self.openNickserv = QAction("NICKSERV", self)
    self.openNickserv.triggered.connect(self.openNickservPM)
    self.helpMenu.addAction(self.openNickserv)

    #Create CALSPRITE button in 'HELP' menu
    self.openCalsprite = QAction("CALSPRITE", self)
    self.openCalsprite.triggered.connect(self.openCalspritePM)
    self.helpMenu.addAction(self.openCalsprite)

    #Create REPORT BUG button in 'HELP' menu
    self.openBugAction = QAction("REPORT BUG", self)
    self.openBugAction.triggered.connect(self.openBug)
    self.helpMenu.addAction(self.openBugAction)

    #Create REMOVE CHUM button in Chum Context menu
    self.removeFriendContext = QAction("REMOVE CHUM")
    self.removeFriendContext.triggered.connect(self.remove_chum)

    #Create BLOCK button in Chum Context menu
    self.blockContext = QAction("BLOCK")
    self.blockContext.triggered.connect(self.block_selected)

def initialize_buttons(self):
    self.nameButton.setIcon(QIcon(self.theme["path"] + "/chummy.png"))
    #Make color picker open on opening of the Color Button
    self.colorButton.clicked.connect(self.color_picker)
    self.mood_buttons = dict()
    #Set stylesheet and set an action for every defined mood button
    #In the dictionary, give it the corresponding Icon
    for num in range(23):
        name = "moodButton{}".format(num)
        if hasattr(self, name):
            button = getattr(self, name)
            self.mood_buttons[num] = button
            mood_name = self.app.moods.getName(num)
            button.setIcon(QIcon(os.path.join(self.theme["path"], mood_name + ".png")))
            button.clicked.connect(self.make_setMood(button))            
    

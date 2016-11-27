from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor
from PyQt5.QtCore import Qt
from quamash import QEventLoop

import asyncio, sys, os.path, json, re
from asyncio import async as aioasync

from gui import Gui
from client import Client
from themes import *
from messages import *
from config import Config, template_config
            
class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        loop = QEventLoop(self)
        self.loop = loop
        asyncio.set_event_loop(loop)

        self.config = Config
        
        self.theme = themes[self.config["lastTheme"]]
        self.theme_name = self.theme["name"]
        self.setStyleSheet(self.theme["styles"])
        self.palette().highlight().setColor(QColor("#CCCCCC"))

        self.friends = self.config["friends"]
        self.users = self.config["users"]
        self.userlist = self.config["userlist"]
        self.userlist.update(self.users)
        self.userlist.update(self.friends)
        self.host = "irc.mindfang.org"
        self.port = 1413
        self.username = self.config['username']
        self.realname = self.config['username']
        self.nick = self.config['defaultuser']
        self.users = self.config['users']
        self.color = self.users[self.nick] if self.nick in self.users.keys() else "#000"

        self.gui = Gui(self.loop, self)
        self.client = Client(self.loop, self.gui, self)
        coro = self.loop.create_connection(lambda: self.client, self.host, self.port)
        aioasync(coro)
        self.gui.initialize()
        loop.run_forever()

    def change_nick(self, nick, color):
        self.nick = nick
        self.change_color(color)
        self.client.send("NICK {}\r\n".format(self.nick))
        self.gui.nameButton.setText(self.nick)
        
        
    def change_color(self, color):
        self.color = color
        self.userlist[self.nick] = color
        self.users[self.nick] = color
        self.gui.colorButton.setStyleSheet('background-color:' + self.color + ';')

    def send_msg(self, msg, user=None):
        process_send_msg(self, msg, user=user)

    def msg_received(self, msg):
        process_received_msg(self, msg)

    def pm_received(self, msg, user):
        tab = self.gui.start_privmsg(user)
        tab.display_text(msg, user=user)

    def connection_lost(self, exc):
        print("Connection lost")

    def exit(self):
        with open("resources/config.json", 'w') as config:
            self.config["friends"] = self.friends
            self.config["users"] = self.users
            self.config["userlist"] = self.userlist
            self.config['username'] = self.username
            self.config['defaultuser'] = self.nick
            self.config['users'] = self.users
            config.write(json.dumps(self.config))
        sys.exit()
        
app = App()

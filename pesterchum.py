from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtCore import Qt
from quamash import QEventLoop

import asyncio, sys, os.path, json, re
from asyncio import async as aioasync
from random import randint

from gui import Gui
from client import Client
from messages import *
            
class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        loop = QEventLoop(self)
        self.loop = loop
        asyncio.set_event_loop(loop)
        
        with open("ui/pesterchum-styles.css") as styles:
            self.styles = styles.read()
            self.setStyleSheet(self.styles)
        with open("resources/config.json", 'r') as config:
            data = config.read()
            if data:
                self.config = json.loads(data)
            else:
                name = "pesterClient" + str(randint(100,700))
                self.config = dict(users={name:"#000"}, lastUser=name, friends={}, username=name, lastTheme="pesterchum2.5")

        self.friends = self.config["friends"]
        self.host = "irc.mindfang.org"
        self.port = 1413
        self.username = self.config['username']
        self.realname = self.config['username']
        self.nick = self.config['lastUser']
        self.users = self.config['users']
        self.color = self.users[self.nick] if self.nick in self.users.keys() else "#000"

        self.gui = Gui(self.loop, self)
        self.client = Client(self.loop, self.gui, self)
        coro = self.loop.create_connection(lambda: self.client, self.host, self.port)
        aioasync(coro)
        self.gui.initialize()
        loop.run_forever()

    def send_msg(self, msg, user=None):
        process_send_msg(self, msg, user=user)

    def msg_received(self, msg):
        process_received_msg(self, msg)

    def pm_received(self, msg, user):
        tab = self.gui.start_privmsg(user)
        tab.userOutput.insertHtml(msg.strip() + "<br />")

    def connection_lost(self, exc):
        print("Connection lost")

    def exit(self):
        with open("resources/config.json", 'w') as config:
            config.write(json.dumps(self.config))
        sys.exit()
        
app = App()

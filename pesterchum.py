from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from quamash import QEventLoop

import asyncio, sys, os.path, json, re

from gui import Gui
from client import Client
from themes import *
from messages import *
from moods import *
from config import Config, template_config, save_config
from options import Options, default_options, save_options
from commands import Commands

from oyoyo import cmdhandler, parse
            
class App(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        #Establish loop as Quamash Event Loop
        loop = QEventLoop(self)
        self.loop = loop
        asyncio.set_event_loop(loop)
        self.connected = False #Set Connection state
        self.idle = False
        self.names_list = dict()
        self.online = []

        #Initialize imports
        self.config = Config
        self.options = Options
        self.moods = Moods(self)
        self.commands = Commands
        self.handler = cmdhandler.CommandHandler(self, self.commands)

        #Initialize theme & styles
        self.themes = themes
        self.change_theme(self.config["lastTheme"])

        #Initialize configurations
        self.friends = self.config["friends"] 
        self.users = self.config["users"]
        self.userlist = self.config["userlist"]
        self.userlist.update(self.users)
        self.userlist.update(self.friends)
        self.blocked = self.config["blocked"]
        self.host = "irc.mindfang.org"
        self.port = 1413
        self.username = "pcc31"
        self.realname = "pcc31"
        self.nick = self.config['defaultuser']
        self.users = self.config['users']
        self.color = self.users[self.nick] if self.nick in self.users.keys() else "#000"

        #Establish Connection and GUI, start the loop
        #Connection is an Asynchronous create_connection, takes
        #A subclass of asyncio.Protocol
        self.gui = Gui(self.loop, self)
        self.client = Client(self.loop, self.gui, self)
        coro = self.loop.create_connection(lambda: self.client, self.host, self.port)
        asyncio.ensure_future(coro)
        self.gui.initialize()
        loop.run_forever()

    def change_theme(self, theme):
        self.theme = themes[theme]
        self.theme_name = self.theme["name"] 
        self.setStyleSheet(self.theme["styles"])
        if hasattr(self, "gui"):
            self.gui.close()
            self.gui = Gui(self.loop, self)
            self.gui.initialize()

    def change_nick(self, nick, color):
        #Change user nickname or 'Chumhandle'
        self.nick = nick
        self.change_color(color)
        self.client.send("NICK {}\r\n".format(self.nick))
        self.gui.nameButton.setText(self.nick)
        
    def change_color(self, color):
        #Change current user's text color
        self.color = color
        self.userlist[self.nick] = color
        self.users[self.nick] = color
        self.gui.colorButton.setStyleSheet('background-color:' + self.color + ';')
        for user in self.userlist.keys():
                    self.send_msg(fmt_color(self.color), user=user)
    def changeMood(self, name):
        #Change current user's mood
        mood = self.moods.getMood(name)
        self.send_msg("MOOD >{}".format(mood), user="#pesterchum")
        self.moods.value = mood
        if type(mood) == str:
            pass
        elif type(mood) == int:
            mood = self.moods.getName(mood)
        else:
            return
        if self.gui.tabWindow:
            for user in self.gui.tabWindow.users:
                self.pm_received(fmt_mood_msg(self, mood, self.nick), user)

    def changeUserMood(self, user, mood):
        #Called when a friend changes their mood, sets the icon in chumsTree
        if type(mood) == str:
            pass
        elif type(mood) == int:
            mood = self.moods.getName(mood)
        else:
            return
        item = self.gui.getFriendItem(user)[0]
        item.setIcon(0, QIcon(os.path.join(self.theme["path"], mood + ".png")))
        if self.gui.tabWindow:
            if user in self.gui.tabWindow.users:
                self.pm_received(fmt_mood_msg(self, mood, user), user)
        
    def getFriendsMoods(self):
        #Called on connection, use GETMOOD command in #pesterchum
        #To request moods of users
        online = set(self.friends.keys()).intersection(self.names_list["#pesterchum"])
        self.online.extend(online)
        msg = "GETMOOD {}".format("".join(online))
        self.send_msg(msg, user="#pesterchum")

    def getFriendMood(self, user):
        #Get a friend's mood
        self.send_msg("GETMOOD {}".format(user))

    def send_msg(self, msg, user=None):
        #Process a message, to user / channel
        process_send_msg(self, msg, user=user)

    def send(self, msg, user=None):
        bargs = []
        for arg in args:
            if isinstance(arg, str):
                bargs.append(arg.encode())
            elif isinstance(arg, bytes):
                bargs.append(arg)
            else:
                raise cmdhandler.IRCClientError('Refusing to send one of the args from provided: %s'
                                     % repr([(type(arg), arg) for arg in args]))

        msg = " ".encode().join(bargs)
        self.client.send(msg + "\r\n".encode())    

    def msg_received(self, msg):
        msgs = msg.split("\n")
        msg2 = msg
        for msg in msgs:
            if msg.strip():
                try:
                    prefix, command, args = parse.parse_raw_irc_command(msg)
                except IndexError:
                    print(msg2)
                if prefix:
                    prefix = parse.parse_nick(prefix.decode())[0]
                try:
                    self.handler.run(command, prefix, *args)
                except cmdhandler.CommandError as e:
                    print(e)

    def pm_received(self, msg, user):
        #Display processed message, called by process_received_msg
        tab = self.gui.start_privmsg(user)
        tab.display_text(msg)

    def pm_begin(self, msg, user):
        #Display pm begin message, begin pm
        #Called when PESTERCHUM:BEGIN received
        #And on PM started
        tab = self.gui.start_privmsg(user)
        tab.display_text(msg)

    def pm_cease(self, msg, user):
        #Called when PM is closed or receive PESTERCHUM:CEASE
        pass

    def add_friend(self, user):
        #Called when the ADD [CHUM] button is clicked and the dialog is answered
        #Add the user to self.friends, get the users color (probably doesnt have)
        #Add a new item to gui.chumsTree Widget
        #Set the icon by default to
        self.userlist[user] = self.getColor(user)
        self.friends[user] = self.getColor(user)
        treeitem = QTreeWidgetItem()
        treeitem.setText(0, user)
        treeitem.setIcon(0, QIcon(self.theme["path"] + "/offline.png"))
        self.gui.chumsTree.addTopLevelItem(treeitem)
        self.getFriendMood(user)

    def remove_friend(self, user, item=None):
        #Called via the Context menu (gui.remove_chum) in chumsTree
        if user in self.friends.keys():
            if item:
                index = self.gui.chumsTree.indexOfTopLevelItem(item)
                self.gui.chumsTree.takeTopLevelItem(index)
            else:
                index = self.gui.chumsTree.indexOfTopLevelItem(self.app.gui.getFriendItem(user)[0])
                self.gui.chumsTree.takeTopLevelItem(index)
            del self.friends[user]

    def send_begin(self, user):
        #Send target user the begin PM command
        self.send_msg("PESTERCHUM:BEGIN", user=user)
        self.send_msg(fmt_color(self.color), user=user)

    def send_cease(self, user):
        #Send target user the cease PM command
        self.send_msg("PESTERCHUM:CEASE", user=user)

    def connection_lost(self, exc):
        #A little glitchy
        #Restart connection on connection lost
        self.connected = False
        self.client.send("QUIT :Disconnected\r\n")
        self.client.transport.close()
        self.client = Client(self.loop, self.gui, self)
        coro = self.loop.create_connection(lambda: self.client, self.host, self.port)
        asyncio.ensure_future(coro)

    def connection_made(self, transport):
        #On connection_made send NICK and USER commands
        nick = "NICK %s\r\n" % self.nick
        user = "USER %s %s %s %s\r\n" % (self.username, self.host, self.host, self.realname)
        self.client.send(nick)
        self.client.send(user)
        for user in self.userlist.keys():
                self.send_msg(fmt_color(self.color), user=user)

    def reconnect(self):
        pass

    def add_blocked(self, user):
        self.blocked.append(user)

    def toggle_idle(self):
        self.idle = not self.idle
        if self.idle and self.gui.tabWindow:
            for user in self.gui.tabWindow.users:
                process_send_msg(self, "PESTERCHUM:IDLE", user=user)
                tab = self.gui.start_privmsg(user)
                tab.display_text(fmt_me_msg(self, "/me is now idle chum!", user=self.nick))
        
    def join(self):
        #Called once the MODE keyword is seen in received messages
        #Joins the #pesterchum channel
        #Gets all friends moods
        join = "JOIN #pesterchum\r\n"
        self.client.send(join)
        self.connected = True

    def getColor(self, user):
        #Get a user's COLOR
        if user in self.userlist.keys():
            return self.userlist[user]
        else:
            self.userlist[user] = "#000000"
            return "#000000"

    def setColor(self, user, color):
        #Set a users COLOR
        self.userlist[user] = color
        if user in self.friends.keys():
            self.friends[user] = color
        
    def exit(self):
        #Called when exiting the client
        #Save configurations and sys.exit
        self.client.send("QUIT :Disconnected\r\n")
        self.config["friends"] = self.friends
        self.config["users"] = self.users
        self.config["userlist"] = self.userlist
        self.config['defaultuser'] = self.nick
        self.config['users'] = self.users
        self.config['blocked'] = self.blocked
        self.config['lastTheme'] = self.theme_name
        save_config(self.config)
        save_options(self.options)
        msg = "QUIT :Disconnected"
        self.client.send(msg)
        sys.exit()
        
PesterClient = App()

import re, os
from datetime import datetime

from formatting import *
from oyoyo import parse

from PyQt5.QtCore import pyqtSignal

def process_commands(*args):
    pass

class Commands:
    def notice(app, nick, chan, msg):
        msg = msg.decode()
        if nick == 'NickServ':
            if app.gui.tabWindow and "nickServ" in app.gui.tabWindow.users:
                fmt = fmt_disp_msg(app, msg, user="nickServ")
                if fmt:
                    app.pm_received(fmt, "nickServ")
            
    def ping(app, user, channel, *args):
        send = "PONG :{}\r\n".format(channel.decode())
        app.client.send(send)

    def join(app, user, channel, *args):
        user = user.decode() if type(user) == bytes else user
        if user in app.friends.keys():
            app.changeUserMood(user, 0)

    def quit(app, user, channel, *args):
        user = user.decode() if type(user) == bytes else user
        if user in app.friends.keys():
            app.changeUserMood(user, "OFFLINE")

    def privmsg(app, user, channel, *args):
        channel = channel.decode()
        message = args[-1].decode()
        user = user.decode() if type(user) == bytes else user
        #If a GETMOOD message to #pesterchum (not a PM with GETMOOD in it) send our mood
        if channel == "#pesterchum":
            if(b"GETMOOD" in args[-1]) and (app.nick.encode() in args[-1]):
                app.send_msg("MOOD >{}".format(app.moods.value), user="#pesterchum")
            #Check for MOOD message from someone we know
            elif b"MOOD" in args[-1]:
                if message.startswith("MOOD >"):
                    mood = message[6:]
                    #If it is a mood, parse
                    mood = mood.strip()
                    mood = int(mood.strip())
                    #Set that users mood
                    app.changeUserMood(user, mood)
            
        #If a PM to us, display message / check if COLOR command
        elif channel == app.nick:
            #If COLOR command, parse and set that user's color
            if "COLOR >" in message:
                colors = message.strip("COLOR >").split(",")
                colors = list(map(int,map(str.strip, colors)))
                app.setColor(user, rgbtohex(*colors))
            else:
                fmt = fmt_disp_msg(app, message, user=user)
                if fmt:
                    app.pm_received(fmt, user)

        else:
            fmt = fmt_disp_memo(app, message, user)
            if fmt:
                app.memo_received(fmt, channel)

    def welcome(app, user, channel, *args):
        app.join()

    def namreply(app, user, channel, *args):
        try:
            user = user.decode() if type(user) == bytes else user
            channel = args[-2].decode()
            if not channel in app.names_list.keys():
                app.names_list[channel] = set()
            names = set(map(bytes.decode, args[-1].split()))
            app.names_list[channel].update(names)
            
        except IndexError as e:
            print(user, channel, *args)

    def endofnames(app, user, channel, *args):
        if args[-2] == b"#pesterchum":
            app.getFriendsMoods()
        else:
            app.memo_add_names(args[-2].decode())

    def liststart(app, server, handle, *info):
        app.channel_field = info.index(b"Channel")
        app.channel_list = dict()
        
    def list(app, server, handle, *info):
        channel = info[app.channel_field].decode()
        if channel != "#pesterchum":
            ucount = int(info[1].decode())
            app.channel_list[channel] = ucount
            app.receive_list(channel, ucount)

    noticeSignal = pyqtSignal()
    pingSignal = pyqtSignal()
    joinSignal = pyqtSignal()
    quitSignal = pyqtSignal()
    privmsgSignal = pyqtSignal()
    welcomeSignal = pyqtSignal()
    namereplySignal = pyqtSignal()
    endofnamesSignal = pyqtSignal()
    liststartSignal = pyqtSignal()
    listSignal = pyqtSignal()
    nameSignal = pyqtSignal()

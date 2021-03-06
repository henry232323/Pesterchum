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

import re, os
from datetime import datetime

from formatting import *
from oyoyo import parse

from PyQt5.QtCore import pyqtSignal

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
        channel = channel.decode()
        user = user.decode() if type(user) == bytes else user
        if channel == "#pesterchum":
            if user in app.friends.keys():
                app.changeUserMood(user, 0)
        else:
            app.memo_joined(user, channel)

    def part(app, user, channel, *args):
        channel = channel.decode()
        user = user.decode() if type(user) == bytes else user
        if channel == "#pesterchum":
            if user in app.friends.keys():
                app.changeUserMood(user, 2)
        else:
            app.memo_parted(user, channel)

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
            if message.startswith("PESTERCHUM:TIME>"):
                app.memo_time(message.split(">")[-1], user, channel)
                return
            fmt = fmt_disp_memo(app, message, user)
            if fmt:
                app.memo_received(fmt, user, channel)

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

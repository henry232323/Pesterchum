import re, os
from datetime import datetime

from formatting import *
from oyoyo import parse

def process_commands(*args):
    pass

def mode(app, user, channel, *args):
    if args[-1] == "+iTx":
        if not app.connected:
            app.join()

def ping(app, user, channel, *args):
    send = "PONG :{}\r\n".format(channel.decode())
    app.client.send(send)

def join(app, user, channel, *args):
    user = user.decode() if type(user) == bytes else user
    if user in app.friends.keys():
        app.changeUserMood(user, 0)
        app.online.append(user)

def quit(app, user, channel, *args):
    user = user.decode() if type(user) == bytes else user
    if user in app.friends.keys():
        app.changeUserMood(user, "OFFLINE")
        app.online.remove(user)

def privmsg(app, user, channel, *args):
    channel = channel.decode()
    message = args[-1].decode()
    user = user.decode() if type(user) == bytes else user
    #If a GETMOOD message to #pesterchum (not a PM with GETMOOD in it) send our mood
    if (channel == "#pesterchum") and (b"GETMOOD" in args[-1]) and (app.nick.encode() in args[-1]):
        app.send_msg("MOOD >{}".format(app.moods.value), user="#pesterchum")
    #Check for MOOD message from someone we know
    if (channel == "#pesterchum") and (user in app.online) and b"MOOD" in args[-1]:
        if message.startswith("MOOD >"):
            mood = message[6:]
            #If it is a mood, parse
            mood = mood.strip()
            mood = int(mood.strip())
            #If its a friend, set that users mood
            if user in app.friends.keys():
                app.changeUserMood(user, mood)        
        
    #If a PM to us, display message / check if COLOR command
    if channel == app.nick:
        #If COLOR command, parse and set that user's color
        if "COLOR >" in message:
            colors = message.strip("COLOR >").split(",")
            colors = list(map(int,map(str.strip, colors)))
            app.setColor(user, rgbtohex(*colors))
        else:
            fmt = fmt_disp_msg(app, message, user=user)
            if fmt:
                app.pm_received(fmt, user)

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

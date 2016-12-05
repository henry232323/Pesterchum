import re, os
from datetime import datetime

from formatting import *

def process_commands(app, parse):
    user, command, args = parse
    if command in command_list:
        cmdfunc = commandDict[command]
        cmdfunc(app, parse)

def mode(app, parse):
    if parse[2][-1] == "+iTx":
        if not app.connected:
            app.join()

def ping(app, parse):
    user, command, args = parse
    send = "PONG :{}\r\n".format(args[0])
    app.client.send(send)

def join(app, parse):
    user, command, args = parse
    if user in app.friends.keys():
        app.changeUserMood(user, 1)
        app.online.append(user)

def quit(app, parse):
    user, command, args = parse
    if user in app.friends.keys():
        app.changeUserMood(user, "OFFLINE")

def privmsg(app, parse):
    user, command, args = parse
    channel = args[-2]
    message = args[-1]
    #If a GETMOOD message to #pesterchum (not a PM with GETMOOD in it) send our mood
    if (channel == "#pesterchum") and ("GETMOOD" in args[-1]) and (app.nick in args[-1]):
        app.send_msg(app, "MOOD >{}".format(app.moods.value), user="#pesterchum")
    #Check for MOOD message from someone we know
    if (channel == "#pesterchum") and (user in app.online) and "MOOD" in args[-1]:
        exp = r"(?<=MOOD >)(.*)(?=\r\n)*".format(app.nick)
        mood = re.search(exp, message)
        #If it is a mood, parse
        if mood:
            mood = mood.group(0).strip()
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

def connected(app, parse):
    app.join()

def names(app, parse):
    user, command, args = parse
    if not args[-2] in app.names_list.keys():
        app.names_list[args[-2]] = set()
    app.names_list[args[-2]].update(set(args[-1].split()))

def end_names(app, parse):
    user, command, args = parse
    if args[-2] == "#pesterchum":
        app.getFriendsMoods()
    
command_list = ["PING",
                "JOIN",
                "QUIT",
                "PRIVMSG",
                "001",
                "353",
                "366"]

commandDict = {"MODE":mode,
               "PING":ping,
               "JOIN":join,
               "QUIT":quit,
               "PRIVMSG":privmsg,
               "001":connected,
               "353":names,
               "366":end_names}

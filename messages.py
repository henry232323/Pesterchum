import re
from datetime import datetime

def process_send_msg(app, msg, user=None):
    if msg.startswith("/e"):
        app.client.send(eval(msg[3:])+"\r\n")
    else:
        if user:
            nmsg = "PRIVMSG {} :{}\r\n".format(user, msg)
            app.client.send(nmsg)
        else:
            app.client.send(msg + "\r\n")

def process_received_msg(app, msg):
    if msg.startswith("PING"):
        nmsg = msg.replace("PING", "PONG")
        app.client.send(nmsg)
    elif msg.startswith(":") and ("PRIVMSG" in msg):
        usergp = re.match(r"(:.*)(?=!)", msg)
        if usergp:
            user = usergp.group(0)[1:]
            print(user)
        exp = r"PRIVMSG {} :(.*)(?=:PESTERCHUM)*".format(app.nick)
        msggp = re.search(exp, msg)
        if msggp:
            pm = msggp.group(0)[10+len(app.nick):]
            pm = color_to_span(pm)
            print(pm)
            app.pm_received(pm, user)
    elif msg.startswith(":PESTERCHUM"):
        print(msg)
    else:
        print(msg)

#PRIVMSG {} : *msg PESTERCHUM:BEGIN
#PRIVMSG {} :COLOR >0,85,127
def color_to_span(msg):
    exp = r'<c=(.*?)>(.*?)</c>'
    subexp = r'(?<=<c=).*?(?=>)'
    hexcodes = re.sub(subexp, isrgb, msg)
    rep = r'<span style="color:\1">\2</c>'
    colors = re.sub(exp, rep, hexcodes)
    colors = re.sub('</c>', '</span>', colors)
    return colors


def fmt_disp_msg(app, msg, user=None):
    if not user:
        user = app.nick
    time = getTime(app)
    init = getInitials(user, b=False)
    fmt = "<span style=\"font_weight: bold;\">[{time}] <span style=\"color:{color};\">{init}: {msg}</span></span><br />".format(time=time, init=init, msg=msg.strip(), color=app.userlist[user])
    return fmt

def getInitials(user, b=True):
    init = user[0].upper()
    for char in user:
        if char.isupper():
            break
    init += char
    if b:
        return "[" + init + "]"
    else:
        return init

def isrgb(match):
    s = match.group(0)
    if s.startswith("#"):
        return rgb(s)
    elif s.startswith("rgb"):
        return s
    else:
        return "rgb(" + s.strip('rgb()') + ")"

def rgb(triplet, type=str):
    if hasattr(triplet, "group"):
        triplet = triplet.group(0)
    triplet = triplet.strip("#")
    digits = '0123456789abcdefABCDEF'
    hexdec = {v: int(v, 16) for v in (x+y for x in digits for y in digits)}
    if type == str:
        return "rgb" + str((hexdec[triplet[0:2]], hexdec[triplet[2:4]], hexdec[triplet[4:6]]))
    else:
        return hexdec[triplet[0:2]], hexdec[triplet[2:4]], hexdec[triplet[4:6]]

def getTime(app):
    time = datetime.utcnow()
    if app.config["timestamp_show_seconds"]:
        fmt = "{hour}:{minute}:{sec}"
    else:
        fmt = "{hour}:{minute}"
    ftime = fmt.format(
                hour=str(time.hour).zfill(2),
                minute=str(time.minute).zfill(2),
                sec=str(time.second).zfill(2))
    return ftime


import re
from datetime import datetime

def process_send_msg(app, msg, user=None):
    if user:
        nmsg = "PRIVMSG {} :{}\r\n".format(user, msg)
        app.client.send(nmsg)
    else:
        app.client.send(msg + "\r\n")

def process_received_msg(app, msg):
    if ("MODE" in msg) and not app.connected:
        app.join()
    elif msg.startswith("PING"):
        nmsg = msg.replace("PING", "PONG")
        app.client.send(nmsg)
    elif msg.startswith(":") and ("PRIVMSG" in msg):
        usergp = re.match(r"(:.*)(?=!)", msg)
        if usergp:
            user = usergp.group(0)[1:]
        exp = r"PRIVMSG {} :(.*)(?=:PESTERCHUM)*".format(app.nick)
        msggp = re.search(exp, msg)
        if msggp:
            pm = msggp.group(0)[10+len(app.nick):]
            if "COLOR >" in pm:
                colors = pm.strip("COLOR >").split(",")
                colors = list(map(int,map(str.strip, colors)))
                app.setColor(user, rgbtohex(*colors))
            else:
                pm = fmt_disp_msg(app, pm, user=user)
                if pm:
                    app.pm_received(pm, user)

def color_to_span(msg):
    exp = r'<c=(.*?)>(.*?)</c>'
    subexp = r'(?<=<c=).*?(?=>)'
    hexcodes = re.sub(subexp, isrgb, msg)
    rep = r'<span style="color:\1">\2</c>'
    colors = re.sub(exp, rep, hexcodes)
    colors = re.sub('</c>', '</span>', colors)
    return colors

def fmt_begin_msg(app, fromuser, touser):
    msg = "/me began pestering {touser} {toInit} at {time}".format(touser=touser, toInit=getInitials(app, touser, c=True), time=getTime(app))
    return fmt_me_msg(app, msg, fromuser)

def fmt_cease_msg(app, fromuser, touser):
    msg = "/me ceased pestering {touser} {toInit} at {time}".format(touser=touser, toInit=getInitials(app, touser, c=True), time=getTime(app))
    return fmt_me_msg(app, msg, fromuser)
    
def fmt_me_msg(app, msg, user):
    me = msg.split()[0]
    suffix = me[3:]
    init = getInitials(app, user, c=True, suffix=suffix)
    predicate = msg[3+len(suffix):].strip()
    fmt = '<span style="color:#646464;font-weight:bold;font-size:12px;">-- {user}{suffix} {init} {predicate}--</span><br />'
    msg = fmt.format(user=user, init=getInitials(app, user, c=True),
                     time=getTime(app),predicate=predicate, suffix=suffix)
    return msg

def fmt_disp_msg(app, msg, user=None):
    if not user:
        user = app.nick
    if "PESTERCHUM:BEGIN" in msg:
        fmt = fmt_begin_msg(app, user, app.nick)
        app.pm_begin(fmt, user)
        msg = None
    elif "PESTERCHUM:CEASE" in msg:
        fmt = fmt_cease_msg(app, user, app.nick)
        app.pm_cease(fmt, user)
        msg = None
    elif msg.startswith("/me"):
        msg = fmt_me_msg(app, msg, user)
    else:
        msg = color_to_span(msg)
        time = getTime(app)
        init = getInitials(app, user, b=False)
        color = app.getColor(user)
        fmt = '<span style="font-weight:bold;color:black;">[{time}] <span style="color:{color};">{init}: {msg}</span></span><br />'
        msg = fmt.format(time=time,init=init,msg=msg.strip(),color=color)
    return msg

def fmt_color(color):
    if type(color) == tuple:  
        return "COLOR >{},{},{}".format(*color)
    else:
        return "COLOR >{},{},{}".format(*rgb(color, type=tuple))

def getInitials(app, user, b=True, c=False, suffix=None):
    init = user[0].upper()
    for char in user:
        if char.isupper():
            break
    init += char
    if suffix:
        init =+ suffix
    if b:
        fin = "[" + init + "]"
    else:
        fin = init
    if c:
        fin = '<span style="color:{color}">{fin}</span>'.format(fin=fin, color=app.getColor(user))
    return fin

def rgbtohex(r,g,b):
    return '#%02x%02x%02x' % (r,g,b)

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


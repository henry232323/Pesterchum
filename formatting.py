import re, os
from datetime import datetime

def color_to_span(msg):
    '''Convert <c=#hex> codes to <span style="color:"> codes'''
    exp = r'<c=(.*?)>(.*?)</c>'
    subexp = r'(?<=<c=).*?(?=>)'
    hexcodes = re.sub(subexp, isrgb, msg)
    rep = r'<span style="color:\1">\2</c>'
    colors = re.sub(exp, rep, hexcodes)
    colors = re.sub('</c>', '</span>', colors)
    return colors

def fmt_begin_msg(app, fromuser, touser):
    '''Format a PM begin message'''
    msg = "/me began pestering {touser} {toInit} at {time}".format(touser=touser, toInit=getInitials(app, touser, c=True), time=getTime(app))
    return fmt_me_msg(app, msg, fromuser)

def fmt_cease_msg(app, fromuser, touser):
    '''Format a PM cease message'''
    msg = "/me ceased pestering {touser} {toInit} at {time}".format(touser=touser, toInit=getInitials(app, touser, c=True), time=getTime(app))
    return fmt_me_msg(app, msg, fromuser)

def fmt_mood_msg(app, mood, user):
    fmt = "/me changed their mood to {} {}"
    path = os.path.join(app.theme["path"], mood.lower() + ".png")
    img = fmt_img(path)
    msg = fmt.format(mood.upper(), img)
    return fmt_me_msg(app, msg, user)

def fmt_me_msg(app, msg, user, time=False):
    '''Format a /me style message i.e.  -- ghostDunk's [GD'S] cat says hi -- (/me's cat says hi)'''
    me = msg.split()[0]
    suffix = me[3:]
    init = getInitials(app, user, c=True, suffix=suffix)
    predicate = msg[3+len(suffix):].strip()
    timefmt = '<span style="color:black;">[{}]</style>'.format(getTime(app)) if time else ""
    fmt = '<b>{timefmt}<span style="color:#646464;"> -- {user}{suffix} {init} {predicate}--</span></b><br />'
    msg = fmt.format(user=user, init=getInitials(app, user, c=True),
                     timefmt=timefmt if app.options["conversations"]["time_stamps"] else "", predicate=predicate, suffix=suffix)
    return msg

def fmt_disp_msg(app, msg, user=None):
    '''Format a message for display'''
    if not user:
        user = app.nick
    #If beginning PM, use BEGIN message
    if "PESTERCHUM:BEGIN" in msg:
        fmt = fmt_begin_msg(app, user, app.nick)
        app.pm_begin(fmt, user)
        msg = None
    #If other user disconnects, use CEASE message
    elif "PESTERCHUM:CEASE" in msg:
        fmt = fmt_cease_msg(app, user, app.nick)
        app.pm_cease(fmt, user)
        msg = None
    #If /me message, use fmt_me_msg
    elif msg.startswith("/me"):
        msg = fmt_me_msg(app, msg, user, time=True)
    #Otherwise convert <c> to <span> and format normally with initials etc
    else:
        msg = color_to_span(msg)
        time = getTime(app)
        init = getInitials(app, user, b=False)
        color = app.getColor(user)
        fmt = '<b><span style="color:black;">{time} <span style="color:{color};">{init}: {msg}</span></span></b><br />'
        msg = fmt.format(time="[" + time + "]" if app.options["conversations"]["time_stamps"] else "",init=init,msg=msg.strip(),color=color)
    return msg

def fmt_img(src):
    return '<img src="{}" />'.format(src)

def fmt_color(color):
    '''Format a color message'''
    if type(color) == tuple:
        return "COLOR >{},{},{}".format(*color)
    else:
        return "COLOR >{},{},{}".format(*rgb(color, type=tuple))

def getInitials(app, user, b=True, c=False, suffix=None):
    '''
    Get colored or uncolored, bracketed or unbracketed initials with
    or without a suffix using a Chumhandle. A suffix being a me style
    ending. i.e. /me's [GD'S]
    '''
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
    '''Convert RGB values to hex code'''
    return '#%02x%02x%02x' % (r,g,b)

def isrgb(match):
    '''Checks if is RGB, formats CSS rgb func'''
    s = match.group(0)
    if s.startswith("#"):
        return rgb(s)
    elif s.startswith("rgb"):
        return s
    else:
        return "rgb(" + s.strip('rgb()') + ")"

def rgb(triplet, type=str):
    '''Converts hex triplet to RGB value tuple or string'''
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
    '''Get current time in UTC based off settings'''
    time = datetime.utcnow()
    if app.options["conversations"]["show_seconds"]:
        fmt = "{hour}:{minute}:{sec}"
    else:
        fmt = "{hour}:{minute}"
    ftime = fmt.format(
                hour=str(time.hour).zfill(2),
                minute=str(time.minute).zfill(2),
                sec=str(time.second).zfill(2))
    return ftime

def fmt_memo_msg(app, msg, user):
    return "<c={color}>{initials}: {msg}</c>".format(
        initials=getInitials(app, user, b=False, c=False),
        color=app.getColor(user),
        msg=msg)

def fmt_disp_memo(app, message, user):
    msg = "<b>{}<b><br />".format(color_to_span(message))
    return msg

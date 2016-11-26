import re

def process_send_msg(app, msg, user=None):
    if msg.startswith("/e"):
        try:
            eval(msg[3:])
        except Exception as e:
            print(e)
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
            app.pm_received(pm, user)
    elif msg.startswith(":PESTERCHUM"):
        print(msg)
    else:
        print(msg)

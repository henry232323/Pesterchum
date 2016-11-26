import asyncio

class Client(asyncio.Protocol):
    def __init__(self, loop, gui, app):
        self.loop = loop
        self.gui = gui
        self.app = app

    def connection_made(self, transport):
        self.sockname = transport.get_extra_info("sockname")
        self.transport = transport
        nick = "NICK %s\r\n" % self.app.nick
        user = "USER %s %s %s %s\r\n" % (self.app.username, self.app.host, self.app.host, self.app.realname)
        join = "JOIN #pesterchum\r\n"
        self.send(nick)
        self.send(user)
        self.send(join)
        
    def connection_lost(self, exc):
        self.app.connection_lost(exc)
        
    def data_received(self, data):
        self.app.msg_received(data.decode())

    def send(self, data):
        self.transport.write(data.encode())

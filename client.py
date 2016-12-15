import asyncio

class Client(asyncio.Protocol):
    def __init__(self, loop, gui, app):
        self.loop = loop
        self.gui = gui
        self.app = app
        self.buffer = bytes()

    def connection_made(self, transport):
        self.sockname = transport.get_extra_info("sockname")
        self.transport = transport
        self.app.connection_made(transport)
        
    def connection_lost(self, exc):
        self.app.connection_lost(exc)
        
    def data_received(self, data):
        self.buffer += data
        pts = self.buffer.split(b"\n")
        self.buffer = pts.pop()
        for el in pts:
            self.app.msg_received(el.decode())

    def send(self, data):
        #Take data, encode it and send, wraps the transport
        self.transport.write(data.encode())

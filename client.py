import asyncio

class Client(asyncio.Protocol):
    def __init__(self, loop, gui, app):
        self.loop = loop
        self.gui = gui
        self.app = app

    def connection_made(self, transport):
        self.sockname = transport.get_extra_info("sockname")
        self.transport = transport
        self.app.connection_made(transport)
        
    def connection_lost(self, exc):
        self.app.connection_lost(exc)
        
    def data_received(self, data):
        self.app.msg_received(data.decode())

    def send(self, data):
        self.transport.write(data.encode())

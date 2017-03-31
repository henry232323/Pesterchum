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

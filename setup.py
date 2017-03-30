#!/usr/bin/python3
# Copyright (c) 2016-2017, rhodochrosite.xyz
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

import sys
from cx_Freeze import setup, Executable

sys.argv.append("build")

include_files = ["resources", "themes", "cfg"]

build_exe_options = {
    "includes": ["PyQt5", "os", "json", "types", "discord", "aiohttp",
                 "requests", "contextlib", "io", "inspect", "traceback", "subprocess",
                 "async_timeout", "asyncio", "asyncio.compat", "asyncio.base_futures",
                 "asyncio.base_events", "asyncio.base_tasks", "asyncio.base_subprocess",
                 "asyncio.proactor_events", "asyncio.constants","asyncio.selector_events",
                 "asyncio.windows_utils"],
    "excludes": ["tkinter", "_tkinter", '_gtkagg', '_tkagg', 'bsddb', 'curses',
                 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                 'unittest', 'idlelib', 'certifi', 'nacl', "_lzma", "_hashlib", "_bz2"],
    "packages":["oyoyo"],
    "include_files":include_files,
    }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Pesterchum-3.5",
    version = "3.5-0.2.0",
    description = "A version of ghostDunk/illuminatedWax's Pesterchum client, built using Asyncio, PyQt5, and Python 3.5. A server specific IRC client built to imitate the Pesterchum chat client as seen in Homestuck.",
    options = {"build_exe": build_exe_options},
    executables = [Executable("pesterchum.py", base=base, icon="resources/pc_chummy.ico")]
        )
        
                        

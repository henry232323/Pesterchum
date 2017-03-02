import sys
from cx_Freeze import setup, Executable
import os

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
        
                        

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

import json, os

themes = dict()

def getThemes():
    '''
    Can be called any time to refresh themes, creates a theme
    for every folder in the themes directory, sets the css file to
    foldername.css
    The folder name defines the Theme name
    All uis located in the ui folder
    More support for themes to come
    '''
    global themes
    themedir = os.listdir("themes")
    for theme in themedir:
        if os.path.isdir("themes/"+theme):
            themes[theme] = dict()
            name = theme + ".css"
            fpath = os.path.join("themes", theme, name)
            path = os.path.join("themes", theme)
            uipath = os.path.join("themes", theme, "ui")
            with open(fpath, "r") as tfile:
                rfile = tfile.read()
            themes[theme]["styles"] = rfile.replace("$path", path.replace("\\", "/"))
            themes[theme]["style_file"] = name
            themes[theme]["style_path"] = fpath
            themes[theme]["path"] = path
            themes[theme]["name"] = theme
            themes[theme]["ui_path"] = uipath
            themes[theme]["ui_dir"] = os.listdir(uipath)

getThemes()

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

from random import randint
import json, os

#If a username is not defined, generate a random 'pesterClient' name
uname = "pesterClient" + str(randint(100, 700))
#Generic template config, used if config is missing or empty
template_config = dict(users={uname:"#000000"},
                   defaultuser=uname,
                   friends=dict(),
                   lastTheme="pesterchum2.5",
                   timestamp_show_seconds=False,
                   userlist=dict(),
                   blocked=list()) 

if not os.path.exists("cfg"):
    os.mkdir("cfg")
if not os.path.exists("cfg/config.json"):
    with open("cfg/config.json", 'w+'):
        pass
with open("cfg/config.json", 'r') as config:
    data = config.read()
if data:
    #If missing any data, fill in from the template
    Config = json.loads(data)
    conf_keys = Config.keys()
    for key in template_config.keys():
        if key not in conf_keys:
            Config[key] = template_config[key]
else: #In case we need to reference the template again
    Config = {key:value for key,value in template_config.items()}

def save_config(config):
    with open("cfg/config.json", 'w') as conffile:    
        conffile.write(json.dumps(config))  

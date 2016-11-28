from random import randint
from copy import deepcopy
import json

uname = "pesterClient" + str(randint(100, 700))
template_config = dict(users={uname:"#000000"},
                   defaultuser=uname,
                   friends=dict(),
                   lastTheme="pesterchum2.5",
                   timestamp_show_seconds=False,
                   userlist=dict()) 

with open("resources/config.json", 'r') as config:
    data = config.read()
if data:
    Config = json.loads(data)
    conf_keys = Config.keys()
    for key in template_config.keys():
        if key not in conf_keys:
            Config[key] = template_config[key]
else:
    Config = deepcopy(template_config)
        

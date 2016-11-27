from random import randint
from copy import deepcopy
import json

name = "pcc31"
uname = "pesterClient" + str(randint(100, 700))
template_config = dict(users={name:"#000"},
                   lastUser=uname,
                   friends=dict(),
                   username=name,
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
        

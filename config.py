from random import randint
import json

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
        

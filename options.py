import json, os

default_options = {
    "chum_list":{
        "hide_offline_chums":False,
        "show_empty_groups":False,
        "show_number_of_online_chums":False,
        "sort_chums":0,
        "low_bandwidth":False
        },
    "conversations":{
        "time_stamps":True,
        "clock_type":1,
        "show_seconds":False,
        "op_and_voice_in_memos":False,
        "use_animated_smilies":False,
        "receive_random_encounters":False,
        },
    "interface":{
        "tabbed_conversations":True,
        "tabbed_memos":True,
        "minimize":0,
        "close":0,
        "blink_taskbar_on_pesters":False,
        "blink_taskbar_on_memos":False
        },
    "theme":{
        "theme":"pesterchum2.5"
        }
    }

confpath = "resources/options.json"
if os.path.exists(confpath):
    with open(confpath, 'r') as options:
        data = options.read()
    Options = json.loads(data)
    opt_keys = Options.keys()
    for key in default_options.keys():
        if key not in opt_keys:
            Options[key] = default_options[key]
        else:
            opt_keys_2 = Options[key].keys()
            for key in default_options[key].keys():
                if key not in opt_keys_2:
                    Options[key][key] = default_options[key][key]
else:
    with open(confpath, 'w') as options:
        options.write(json.dumps(default_options))

    with open(confpath, 'r') as options:
        data = options.read()
    Options = json.loads(data)

import json, os

themes = dict()

def getThemes():
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

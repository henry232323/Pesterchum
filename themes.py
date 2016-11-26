import json, os

themes = dict()

themedir = os.listdir("themes")
for theme in themedir:
    with open("themes/" + theme, "r") as tfile:
        themes[theme[:-5]] = json.loads(tfile.read())



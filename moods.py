class Moods(object):
    moods = ["chummy", "rancorous", "offline", "pleasant", "distraught",
             "pranky", "smooth", "ecstatic", "relaxed", "discontent",
             "devious", "sleek", "detestful", "mirthful", "manipulative",
             "vigorous", "perky", "acceptant", "protective", "mystified",
             "amazed", "insolent", "bemused"]
    
    def __init__(self, app):
        self.usermoods = dict()
        self.value = 0

    def getMood(self, name):
        name = "offline" if name.lower() == "abscond" else name
        return self.moods.index(name.lower())

    def getName(self, index):
        return self.moods[index]


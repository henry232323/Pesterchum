class Moods(object):
    def __init__(self, app):
        self.moods = ["chummy", "rancorous", "offline", "pleasant", "distraught",
             "pranky", "smooth", "ecstatic", "relaxed", "discontent",
             "devious", "sleek", "detestful", "mirthful", "manipulative",
             "vigorous", "perky", "acceptant", "protective", "mystified",
             "amazed", "insolent", "bemused"]

        self.usermoods = dict()
        self.value = 0

    def getMood(self, name):
        name = "offline" if name.lower() == "abscond" else name
        return self.moods.index(name.lower())

    def getName(self, index):
        return self.moods[index]


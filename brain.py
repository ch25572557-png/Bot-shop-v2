import json

class Brain:
    def __init__(self):
        self.reload()

    def reload(self):
        self.data = json.load(open("config.json","r",encoding="utf-8"))

    def get(self, path):
        v = self.data
        for p in path.split("."):
            v = v[p]
        return v

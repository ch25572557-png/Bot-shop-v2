import json

class Brain:
    def __init__(self):
        self.reload()

    def reload(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, path):
        v = self.data
        for p in path.split("."):
            v = v[p]
        return v

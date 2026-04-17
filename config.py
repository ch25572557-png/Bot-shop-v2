import json

class Config:
    def __init__(self):
        with open("config.json","r") as f:
            self.data = json.load(f)

    def get(self,key):
        v = self.data
        for k in key.split("."):
            v = v[k]
        return v

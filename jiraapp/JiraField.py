

from dataclasses import dataclass
import json



class JiraField:
    name: str
    def __init__(self,name):
        self.name = name
        pass
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True)
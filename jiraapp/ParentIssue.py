from dataclasses import dataclass
import json



class ParentIssue:
    name: str
    def __init__(self,key):
        self.key = key
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True)
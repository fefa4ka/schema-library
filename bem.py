from pathlib import Path
import importlib
from settings import BLOCKS_PATH

class Loader:
    def __init__(self, name, parts, **kwargs):
        self.name = name
        self.parts = parts
        self.base = importlib.import_module(BLOCKS_PATH + '.' + self.name).Base        
        self.mods = {}
        self.models = []

        for mod, value in kwargs.items():
            module_file = Path(BLOCKS_PATH) / self.name / ('_' + mod) / (value + '.py')

            if module_file.exists():
                Module = importlib.import_module(BLOCKS_PATH + '.' + self.name + '._' + mod + '.' + value)
                self.models.append(Module.Modificator)
                self.mods[mod] = value

    @property
    def block(self):
        Models = (self.base,) if len(self.models) == 0 else tuple(self.models)

        return type(self.name,
                    Models,
                    {
                        'name': self.name,
                        'mods': self.mods,
                        'part': self.parts
                    })


class Block:
    def __init__(self, name, parts, **kwargs):
        self.part = parts
        self.name = name
        self.mods = {}

    def __str__(self):
        body = [self.name]
        for key, value in self.mods.items():
            body.append(key + ' = ' + value)
        
        return '\n'.join(body)
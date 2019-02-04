import sys
import glob
import importlib
from pathlib import Path
from collections import defaultdict

from .base import Block
from .builder import Build
from PySpice.Unit import *

def get_bem_blocks():
    blocks = defaultdict()
    for file in glob.glob('./blocks/*/__init__.py'):
        block = file.split('/')[2]
        # base = Path(file).exists() and importlib.import_module(file[2:].replace('/', '.')).Base
        
        blocks[block] = defaultdict(list)
        
        for mod_type, mod_value in [(mod.split('/')[3], mod.split('/')[4]) for mod in glob.glob('./blocks/%s/_*/*.py' % block)]:
            mod_type = mod_type[1:]
            mod_value = mod_value.replace('.py', '')
            blocks[block][mod_type].append(mod_value)

    return blocks

_self = sys.modules[__name__]

for name in get_bem_blocks().keys():
    def build(name=name, *arg, **kwarg):
        return Build(name, *arg, **kwarg).block

    setattr(_self, name, build)
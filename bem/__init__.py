import sys
import glob
import importlib
from pathlib import Path
from collections import defaultdict

from .base import Block, u, is_tolerated
from .builder import Build
from PySpice.Unit import *

def get_bem_blocks(parent=''):
    blocks = defaultdict()
    block = './blocks/' + parent

    for file in glob.glob(block + '/*/__init__.py'):        
        element = file.split('/')[-2]
        
        blocks[element] = defaultdict(list)
        
        for mod_type, mod_value in [(mod.split('/')[-2], mod.split('/')[-1]) for mod in glob.glob(block + '/%s/_*/*.py' % element)]:
            if mod_value.find('_test.py') != -1:
                continue

            mod_type = mod_type[1:]
            mod_value = mod_value.replace('.py', '')
            
            blocks[element][mod_type].append(mod_value)
        
        
        if not parent:
            elements = get_bem_blocks(element)
            if len(elements.keys()):
                blocks[element + '.'] = elements

    return blocks


# def u(unit):
#     """Absolute float value of PySpice.Unit
#     """

#     return float(unit.convert_to_power())

_self = sys.modules[__name__]

blocks = get_bem_blocks()
for name in blocks.keys():
    if name[-1] == '.':
        for element in blocks[name].keys():
            element = name + element
            def build(name=element, *arg, **kwarg):
                return Build(name, *arg, **kwarg).block

            setattr(_self, element.replace('.', '_'), build)
            
    else:
        def build(name=name, *arg, **kwarg):
            return Build(name, *arg, **kwarg).block

        setattr(_self, name, build)
    
    
    

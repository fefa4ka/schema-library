import sys
import glob
import importlib
from pathlib import Path
from collections import defaultdict

from .base import Block
from .util import u, is_tolerated
from .signal import Net
from .builder import Build
from .stockman import Stockman
from PySpice.Unit import *


def get_bem_packs(root='./blocks/*', parent=''):
    blocks = defaultdict(dict)

    for file in glob.glob(root + '/' + parent + '/*/__init__.py'):
        root = '/'.join(file.split('/')[:-2])
        tail = file.split('/') 
        pack = tail[2]
        element = tail[-2]
        
        blocks[pack][element] = defaultdict(list)
        
        for mod_type, mod_value in [(mod.split('/')[-2], mod.split('/')[-1]) for mod in glob.glob(root + '/%s/_*/*.py' % element)]:
            if mod_value.find('_test.py') != -1:
                continue

            mod_type = mod_type[1:]
            mod_value = mod_value.replace('.py', '')
            
            blocks[pack][element][mod_type].append(mod_value)
        
        
        if not parent:
            elements = get_bem_packs(root, element)
            if len(elements.keys()):
                blocks[pack][element + '.'] = elements[pack]

    return blocks


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


packs = get_bem_packs()

for pack in packs.keys():
    blocks = {}
    
    for name in packs[pack].keys():
        if name[-1] == '.':
            for element in packs[pack][name].keys():
                element = name + element
                def build(name=pack + '.' + element, *arg, **kwarg):
                    return Build(name, *arg, **kwarg).block

                block_name = element.replace('.', '_')
                blocks[block_name] = build
                
        else:
            def build(name=pack + '.' + name, *arg, **kwarg):
                return Build(name, *arg, **kwarg).block

            blocks[name] = build


    sys.modules[__name__ + '.' + pack] = type(pack, (object,), blocks)
        
    
    

import importlib
import logging
from pathlib import Path

from settings import BLOCKS_PATH
from .base import Block as BaseBlock
from skidl import TEMPLATE
from inspect import getmro
from collections import OrderedDict

logger = logging.getLogger(__name__)

    
class Build:
    name = None
    base = None
    mods = {}
    props = {}
    models = {}
    files = []

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.mods = {}
        self.props = {}
        self.models = []
        self.inherited = []
        # self.files = []
        
        block_dir = self.name.replace('.', '/')

        base_file = Path(BLOCKS_PATH) / block_dir / ('__init__.py')
        self.base = base_file.exists() and importlib.import_module(BLOCKS_PATH + '.' + self.name).Base        
        
        if self.base:
            # if type(self.base.files) == list:
            #     self.files = self.base.files 
                
            # self.files.append(str(base_file))

            for mod, value in kwargs.items():
                if type(value) == list:
                    self.mods[mod] = value
                else:
                    value = str(value)
                    self.mods[mod] = value.split(',')
            
            for mod, value in self.base.mods.items():
                if not self.mods.get(mod, None):
                    self.mods[mod] = value

            for mod, values in self.mods.items():
                if type(values) != list:
                    values = [str(values)]

                for value in values:
                    for mod_block_dir in set([block_dir]):
                        module_file = Path(BLOCKS_PATH) / mod_block_dir / ('_' + mod) / (value + '.py')
                        if module_file.exists():
                            # self.files.append(str(module_file))
                            Module = importlib.import_module(BLOCKS_PATH + '.' + mod_block_dir.replace('/', '.') + '._' + mod + '.' + value)
                            self.models.append(Module.Modificator)
                        else:
                            self.props[mod] = value
  
            for key, value in self.props.items():
                del self.mods[key]
        else:
            self.props = kwargs

    # self.files = list(set(self.files))
    # Run once
    def ancestors(self, ancestor=None):
        if not ancestor:
            self.inherited = []

        ancestor = ancestor or self.base
        mods = ancestor.mods if ancestor else self.mods
        for parent in ancestor.inherited:
            ParentBlock = parent(**mods)
            self.inherited += getmro(ParentBlock)[1:-1]
            self.ancestors(ParentBlock)

        return list(OrderedDict.fromkeys(self.inherited))

    @property
    def block(self):
        if self.base:
            Models = self.models
            
            Models.reverse()
           
            if self.base not in Models:
                Models.append(self.base)

            Models += self.ancestors() 
            
        else:
            Models = [BaseBlock]
            
        self.inherited = []
        
        # name = self.name[self.name.find('.') + 1:]
        Block = type(self.name,
                    tuple(Models),
                    {
                        'name': self.name,
                        # 'inher': self.inherited,
                        'mods': self.mods,
                        'props': self.props,
                        # 'files': self.files
                    })

        return Block

    @property
    def element(self):
        return self.block().element

    @property
    def spice(self):
        from skidl import SKIDL, SPICE, set_default_tool, SchLib, Part
        from skidl.tools.spice import set_net_bus_prefixes
        
        set_default_tool(SPICE) 
        set_net_bus_prefixes('N', 'B')
        _splib = SchLib('pyspice', tool=SKIDL)
        
        for p in _splib.get_parts():
            if self.name == p.name or (hasattr(p, 'aliases') and self.name in p.aliases):
                return p
            
        if self.name.find(':') != -1:
            kicad, spice = self.name.split(':')

            return Part(kicad, spice, dest=TEMPLATE)

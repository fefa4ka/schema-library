import importlib
import logging
from pathlib import Path
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from settings import BLOCKS_PATH
from .base import Block as BaseBlock
from .tester import Test as BaseTest

logger = logging.getLogger(__name__)

    
class Build:
    name = None
    base = None
    mods = {}
    props = {}
    models = {}
    files = []
    tests = []

    def __init__(self, name, debug=None, *args, **kwargs):
        self.name = name
        self.mods = {}
        self.props = {}
        self.models = []
        self.files = []
        self.tests = []
        
        self.debug = debug

        block_dir = self.name.replace('.', '/')

        base_file = Path(BLOCKS_PATH) / block_dir / ('__init__.py')
        self.base = base_file.exists() and importlib.import_module(BLOCKS_PATH + '.' + self.name).Base        
        
        base_test = Path(BLOCKS_PATH) / block_dir / ('test.py')
        BaseTest = base_test.exists() and importlib.import_module(BLOCKS_PATH + '.' + self.name + '.test')
        if BaseTest:
            self.tests.append(BaseTest.Case)
        elif self.name.find('.') != -1:
            parent = self.name.split('.')[0]
            base_test = Path(BLOCKS_PATH) / parent / ('test.py')
            BaseTest = base_test.exists() and importlib.import_module(BLOCKS_PATH + '.' + parent + '.test')
            if BaseTest:
                self.tests.append(BaseTest.Case)


        if self.base:
            self.files.append(str(base_file))

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
                    module_file = Path(BLOCKS_PATH) / block_dir / ('_' + mod) / (value + '.py')
                    if module_file.exists():
                        self.files.append(str(module_file))
                        Module = importlib.import_module(BLOCKS_PATH + '.' + self.name + '._' + mod + '.' + value)
                        self.models.append(Module.Modificator)

                        test_file = Path(BLOCKS_PATH) / block_dir / ('_' + mod) / (value + '_test.py')
                        if test_file.exists():
                            Test = importlib.import_module(BLOCKS_PATH + '.' + self.name + '._' + mod + '.' + value + '_test')
                            self.tests.append(Test.Case) 
                    else:
                        self.props[mod] = value

            for key, value in self.props.items():
                del self.mods[key]
        else:
            self.props = kwargs

    @property
    def block(self):
        if self.base:
            Models = self.models
            Models.reverse()
            if self.base not in Models:
                Models.append(self.base)
            Models = tuple(self.models)
        else:
            Models = (BaseBlock, )

        if len(self.tests):
            Tests = self.tests
            # Tests.reverse()
            Tests = tuple(set(self.tests))
        else:
            Tests = (BaseTest,)
            
        Block = type(self.name,
                    Models,
                    {
                        'name': self.name,
                        'mods': self.mods,
                        'props': self.props,
                        'test': type(self.name + 'Test', Tests, {}),
                        'DEBUG': self.debug if self.debug != None else builtins.DEBUG,
                        'files': self.files
                    })

        return Block

    @property
    def element(self):
        return self.block().element

    @property
    def spice(self):
        from skidl import SKIDL, SPICE, set_default_tool, SchLib
        from skidl.tools.spice import set_net_bus_prefixes
        
        set_default_tool(SPICE) 
        set_net_bus_prefixes('N', 'B')
        _splib = SchLib('pyspice', tool=SKIDL)
        
        for p in _splib.get_parts():
            if self.name == p.name or (hasattr(p, 'aliases') and self.name in p.aliases):
                return p

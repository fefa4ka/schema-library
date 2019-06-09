import os
import sys

# KiCad path for skidl
# KiCad Modules directory
os.environ['KISYSMOD'] = './kicad/modules'
os.environ['KICAD_SYMBOL_DIR'] = './kicad/library'
# Path where is libngspice.dylib placed
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/Cellar/libngspice/28/lib/'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKS_PATH = 'blocks'


# Digital Units
from PySpice.Unit.Unit import Unit
from PySpice.Unit import u_Degree, _build_unit_shortcut
class Byte(Unit):
    __unit_name__ = 'byte'
    __unit_suffix__ = 'B'
    __quantity__ = 'byte'
    __default_unit__ = False 

_build_unit_shortcut(Byte())


# Default simulation settings
default_temperature = [-30, 0, 25] @ u_Degree
params_tolerance = 0.1
test_sources =[{
    'name': 'SINEV',
    'args': {
        'amplitude': {
            'value': 10,
            'unit': {
                'name': 'volt',
                'suffix': 'V'
            }
        },
        'frequency': {
            'value': 120,
            'unit': {
                'name': 'herz',
                'suffix': 'Hz'
            }
        }
    },
    'pins': {
        'p': ['input'],
        'n': ['output', 'gnd']
    }
}]
    
test_body_kit = [{
    'name': 'basic.RLC',
    'mods': {
        'series': ['R']
    },
    'args': {
        'R_series': {
            'value': 1000,
            'unit': {
                'name': 'ohm',
                'suffix': 'Ω'
            }
        }
    },
    'pins': {
        'input': ['output'],
        'output': ['gnd']
    }
}, {
    'name': 'basic.source.VS',
    'mods': {
        'flow': ['SINEV']
    },
    'args': {
        'V': {
            'value': 12,
            'unit': {
                'name': 'volt',
                'suffix': 'V'
            }
        },
        'frequency': {
            'value': 60,
            'unit': {
                'name': 'herz',
                'suffix': 'Hz'
            }
        }
    },
    'pins': {
        'input': ['input'],
        'output': ['gnd']
    }
}]


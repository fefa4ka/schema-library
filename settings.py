import os
import sys
# KiCad path for skidl

# KiCad Modules directory
os.environ['KISYSMOD'] = '/Library/Application Support/kicad/modules'
os.environ['KICAD_SYMBOL_DIR'] = '/Library/Application Support/kicad/library'
# Path where is libngspice.dylib placed
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/Cellar/libngspice/28/lib/'

# Digital Units
from PySpice.Unit.Unit import Unit
from PySpice.Unit import _build_unit_shortcut
class Byte(Unit):
    __unit_name__ = 'byte'
    __unit_suffix__ = 'B'
    __quantity__ = 'byte'
    __default_unit__ = True

_build_unit_shortcut(Byte())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Default settings

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

builtins.DEBUG = True  # Turn on for SPICE Simulation

manage = {
    'mount': 'smd_default',  # auto, smd_only, tht_default, tht_only,
    'available': True
}


# Available parts
from PySpice.Unit import u_pF, u_V, u_uF, u_Ohm, u_kOhm, u_MHz, u_mA, u_mW

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
    
test_load = [{
    'name': 'RLC',
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
}]

parts = {
    'Capacitor': [
        {
            'mount': 'smd',
            'material': 'ceramic',
            'polarized': False,
            'footprint': 'Capacitor_SMD:C_0805_2012Metric',
            'values': [10 @ u_pF, 22 @ u_pF, 33 @ u_pF, 100 @ u_pF, 220 @ u_pF, 470 @ u_pF, 1000 @ u_pF, 2200 @ u_pF, 3300 @ u_pF, 4700 @ u_pF, 0.01 @ u_uF, 0.015 @ u_uF, 0.022 @ u_uF, 0.047 @ u_uF, 0.1 @ u_uF, 0.22 @ u_uF, 0.33 @ u_uF, 0.47 @ u_uF, 0.68 @ u_uF, 1 @ u_uF, 2.2 @ u_uF, 10 @ u_uF],
        },
        {
            'mount': 'tht',
            'material': 'ceramic',
            'polarized': False,
            'footprint': 'Capacitor_SMD:C_0805_2012Metric',
            'values': [10 @ u_pF, 22 @ u_pF, 33 @ u_pF, 100 @ u_pF, 220 @ u_pF, 470 @ u_pF, 1000 @ u_pF, 2200 @ u_pF, 3300 @ u_pF, 4700 @ u_pF, 0.01 @ u_uF, 0.015 @ u_uF, 0.022 @ u_uF, 0.047 @ u_uF, 0.1 @ u_uF, 0.22 @ u_uF, 0.33 @ u_uF, 0.47 @ u_uF, 0.68 @ u_uF, 1 @ u_uF, 2.2 @ u_uF, 10 @ u_uF],
        },
        {
            'mount': 'tht',
            'material': 'aluminium',
            'footprint': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',
            'polarized': True,
            'values': [1 @ u_uF, 10 @ u_uF, 100 @ u_uF, 220 @ u_uF, 470 @ u_uF]
        }
    ],
    'Resistor': [
        {
            'mount': 'tht',
            'footprint': 'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal',
            'values': [value @ u_Ohm for value in range(1, 91)] + [value @ u_Ohm for value in range(100, 910, 10)] + [value / 10. @ u_kOhm for value in range(10, 91)] + [value @ u_kOhm for value in range(10, 91)] + [value @ u_kOhm for value in range(100, 910, 10)]
        },
        {
            'mount': 'smd',
            'package': '0805',
            'footprint': 'Resistor_SMD:R_0805_2012Metric',
            'values': [value @ u_Ohm for value in range(1, 91)] + [value @ u_Ohm for value in range(100, 910, 10)] + [value / 10. @ u_kOhm for value in range(10, 91)] + [value @ u_kOhm for value in range(10, 91)] + [value @ u_kOhm for value in range(100, 910, 10)]
        }
    ],
    'Inductor': [
        {
            'mount': 'tht',
            'footprint': 'Inductor_THT:L_Axial_L6.6mm_D2.7mm_P10.16mm_Horizontal_Vishay_IM'
        }
    ],
    'Diode': [
        {
            'mount': 'smd',
            'footprint': 'Diode_SMD:D_MiniMELF'
        }
    ],
    # BC337 BC327 A1015 C1815 S8050 S8550 2N3906 2N2907 2N2222
    # 20×BC337 Bipolar (BJT) Transistor NPN 45V 800mA 100MHz 625mW Through Hole TO-92-3
    # 20×BC327 Bipolar (BJT) Transistor PNP 45V 800mA 100MHz 625mW Through Hole TO-92-3
    # 20×2N2222 Bipolar (BJT) Transistor NPN 40V 600mA 200MHz 625mW Through Hole TO-92-3
    # 20×2N2907 Bipolar (BJT) Transistor PNP 40V 600mA 200MHz 625mW Through Hole TO-92-3
    # 20×2N3904 Bipolar (BJT) Transistor NPN 40V 200mA 200MHz 625mW Through Hole TO-92-3
    # 20×2N3906 Bipolar (BJT) Transistor PNP 40V 200mA 200MHz 625mW Through Hole TO-92-3
    # 20×S8050 Bipolar (BJT) Transistor NPN 25V 0.5A 100MHz 1W Through Hole TO-92-3
    # 20×S8550 Bipolar (BJT) Transistor PNP 25V 0.5A 100MHz 1W Through Hole TO-92-3
    # 20×A1015 Bipolar (BJT) Transistor PNP 50V 150mA 80MHz 400mW Through Hole TO-92-3
    # 20×C1815 Bipolar (BJT) Transistor NPN 50V 150mA 80MHz 400mW Through Hole TO-92-3
    'Transistor': [
        {
            'mount': 'tht',
            'bipolar': 'npn',
            'model': '2n2222a',
            'footprint': 'Package_TO_SOT_THT:TO-92',
        },
        {
            'mount': 'tht',
            'bipolar': 'npn',
            'model': 'bc327',
            'footprint': 'Package_TO_SOT_THT:TO-92',
            'datasheet': 'https://www.onsemi.com/pub/Collateral/BC337-D.PDF'
        }
    ],
    'Transformer': [
        {
            'mount': 'tht',
            'footprint': 'Transformer_THT:Transformer_37x44'
        }
    ]
}


# Blocks
BLOCKS_PATH = 'blocks'


# Logging

import os
import sys
# KiCad path for skidl

# KiCad Modules directory
os.environ['KISYSMOD'] = '/Users/fefa4ka/Development/_clone/kicad/modules'
os.environ['KICAD_SYMBOL_DIR'] = '/Users/fefa4ka/Development/_clone/kicad/library'

# Path where is libngspice.dylib placed
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/Cellar/libngspice/28/lib/'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Default settings
DEBUG = True  # Turn on for SPICE Simulation

manage = {
    'mount': 'smd_default',  # auto, smd_only, tht_default, tht_only,
    'available': True
}


# Available parts
from PySpice.Unit import u_pF, u_uF, u_Ohm, u_kOhm

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

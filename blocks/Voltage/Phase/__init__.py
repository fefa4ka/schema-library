from bem import Block, Build
from skidl import Net, subcircuit
# from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Block):
    mods = {
        'split': ['unity']
    }

    pins = {
        'v_ref': True,
        'input': ('Some', ['output']),
        'output_n': True,
        'gnd': True
    }
    
    def circuit(self):
        pass 
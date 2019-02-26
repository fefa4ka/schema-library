from bem import Block, Build
from skidl import Net, subcircuit
# from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Block):
    mods = {
        'split': ['unity']
    }
    
    def __init__(self):
        # self.input = input

        self.circuit()

    
    def circuit(self):
        self.gnd = Net()
        self.v_ref = Net()
        self.input = self.output = Net()
        
        self.output_n = Net()

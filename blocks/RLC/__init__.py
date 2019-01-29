from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_F, u_H

available_parts = [1 @ u_Ohm, 1 @ u_F, 1 @ u_H]

class Base(Block):
    def __init__(self, *args, **kwargs):
        
        self.circuit(*args, **kwargs)

    
    def circuit(self):
        self.v_ref = Net('RLCV')
        self.gnd = Net()
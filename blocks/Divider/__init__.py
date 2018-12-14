from bem import Block
from PySpice.Unit import u_kOhm, u_V

class Base(Block):
    # Props
    V_in = 0
    V_out = 0
    
    def __init__(self, V_in, V_out):
        self.V_in = V_in
        self.V_out = V_out

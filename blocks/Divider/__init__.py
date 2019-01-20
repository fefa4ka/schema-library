from bem import Block, Build
from PySpice.Unit import u_Ohm, u_V, u_A

class Base(Block):
    """Voltage Divider

    Voltage divider from `V_in` to `V_out` could be implemented in different ways
    and provide current `I_out`.
    
    Arguments:
        Block {[type]} -- [description]
    """

    # Props
    V_in = 10 @ u_V
    V_out = 3 @ u_V
    I_out = 0.05 @ u_A

    R_in = 0 @ u_Ohm
    R_out = 0 @ u_Ohm

    def __init__(self, V_in, V_out, I_out):
        self.V_in = V_in
        self.V_out = V_out
        self.I_out = I_out

        self.circuit()
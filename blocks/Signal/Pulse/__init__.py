from bem import Block, u_s
from skidl import Net

class Base(Block):
    """**Pulser**

    Pulse triggered when some event occur.
    """

    mods = {
        'onHigh': ['fixed']
    }

    width = 0.03 @ u_s

    def __init__(self, width=None, input=None):
        self.input = input

        self.circuit()

    
    def circuit(self):
        self.input = self.output = self.input or Net('PulseGeneratorInput')

        self.v_ref = Net()
        self.gnd = Net()

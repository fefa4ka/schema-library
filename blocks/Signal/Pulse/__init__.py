from bem import Block, u_s
from skidl import Net

class Base(Block):
    """**Pulser**

    Pulse triggered when some event occur.
    """

    mods = {
        'highOn': ['fixed']
    }

    width = 0.03 @ u_s

    pins = {
        'v_ref': True,
        'gnd': True
    }

    def willMount(self, width=None, input=None):
        self.input = input
    
    def circuit(self):
        self.input = self.output = self.input or Net('PulseGeneratorInput')

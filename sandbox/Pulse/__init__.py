from bem.abstract import Electrical
from bem import Net, u_s

class Base(Electrical()):
    """**Pulser**

    Pulse triggered when some event occur.
    """

    width = 0.03 @ u_s

    pins = {
        'v_ref': True,
        'gnd': True
    }

    def willMount(self, width=None, input=None):
        self.input = input
    
    def circuit(self):
        self.input = self.output = self.input or Net('PulseGeneratorInput')

from bem import Build, Net
from bem.abstract import Physical, Network
from skidl import Part, TEMPLATE
from skidl.Net import Net as NetType
from PySpice.Unit import u_Ohm, u_uF, u_H, u_kHz

class Base(Physical(), Network(port='two')):
    """**Op Amp**
    
    """
    
    pins = {
        'input': True,
        'input_n': True,
        'v_ref': True,
        'output': True,
        'gnd': True
    }

    def willMount(self):
        pass
    
    def circuit(self):
        self.element = self.part()

        # part['input'] += self.input
        # part['input_n'] += self.input_n
        # part['output'] += self.output
        # part['v_ref'] += self.v_ref
        # part['gnd'] += self.gnd

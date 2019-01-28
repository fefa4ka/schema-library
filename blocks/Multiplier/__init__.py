from bem import Block, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_ms, u_V, u_A, u_Hz, u_Ohm

class Base(Block):
    scale = 2

    V_out = 20 @ u_V
    V_ripple = 1 @ u_V

    R_load = 1000 @ u_Ohm
    I_load = 0 @ u_A
    frequency = 120 @ u_Hz

    def __init__(self, scale, frequency, V_out, V_ripple, R_load, I_load):
        self.V_out = V_out
        self.scale = int(scale)
        self.frequency = frequency
        self.V_ripple = V_ripple
        self.R_load = R_load
        self.I_load = I_load

        self.circuit()

    def circuit(self):
        HalfBridge = Build('DiodeBridge', wave='half', rectifier='full').block
    
        self.input = Net()
        self.output = Net()
        self.gnd = self.input_n = self.output_n = Net()

        sections = []
        
        if self.scale % 2:
            sections.append((self.input_n, self.input))
        else:
            sections.append((self.input, self.input_n))
        
        for block in range(self.scale):
            last = sections[-1]

            half = HalfBridge(V_out=self.V_out, frequency=self.frequency, V_ripple=self.V_ripple, R_load=self.R_load, I_load=self.I_load)
            half.gnd += last[0]
            half.input += last[1]
            
            sections.append((half.input, half.output))

        self.output += sections[-1][1]
        

    def test_sources(self):
        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 120,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }]
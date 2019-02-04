from bem import Block, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_A, u_V

class Base(Block):
    """***Switch**
    
    Switch connected series to the signal.
    """

    V_ref = 0 @ u_V
    V_input = 0 @ u_V
    I_load = 0 @ u_A

    # load = None

    def __init__(self, V_ref=None, V_input=None, I_load=None, *args, **kwargs):
        if not self.gnd:
            self.gnd = Net()

        if self.DEBUG:
            self.load = Resistor()(value = 330, ref = 'R_switch_load')
        
        self.input = Net('SwitchController')
        self.output = Net('SwitchLoadP')
        self.output_n = Net('SwitchLoadN')

        self.circuit(*args, **kwargs)

    @property
    def part(self):
        if self.DEBUG:
            return

        return Part('Switch', 'SW_DPST', footprint=self.footprint, dest=TEMPLATE)

    def circuit(self):
        
        self.v_ref = Net()

        # self.output += self.load.input
        # self.output_n += self.load.output

        # attach_load = self.output & self.load & self.output_n & self.gnd

        if not self.DEBUG:
            switch = self.part()
            
            self.input += switch['1,3']
            self.output += switch['2,4']
    
            
    def test_sources(self):
        return [{
            'name': 'PULSEV',
            'description': "Pulsed voltage source",
            'args': {
                'initial_value': {
                    'value': 0.1,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'pulsed_value': {
                    'value': 10,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'pulse_width': {
                    'value': 0.01,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                },
                'period': {
                    'value': 0.02,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                }
            },
            'pins': {
                'p': ['input'],
                'n': ['gnd']
            }
        }, {
                'name': 'V',
                'args': {
                    'value': {
                        'value': 15,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_ref'],
                    'n': ['gnd']
                }
        }]
    
    def test_load(self):
        return []
            
            
            

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
                        'value': 10,
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
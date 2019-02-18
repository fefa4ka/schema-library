from bem import Block, Build
from skidl import Net, subcircuit


class Base(Block):
    inputs = []
    outputs = []

    def __init__(self, inputs=None):
        default_input = [Net()]
        if self.DEBUG:
            self.input_b = Net()
            default_input = [Net(), self.input_b]

        self.inputs = self.outputs = inputs or default_input

        self.circuit()

    def circuit(self):
        
        self.v_ref = Net()
        self.gnd = Net()

    @property
    def input(self):
        return self.inputs[0]

    @property
    def output(self):
        return self.outputs[0]

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
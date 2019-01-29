from bem import Block, Build
from skidl import Net, subcircuit


class Modificator(Block):
    def create_bridge(self):
        D = Build('Diode').block
        
        circuit = self.output_n & (
            (D()['A,K'] & self.input & D()['A,K']) 
            | (D()['A,K'] & self.input_n & D()['A,K']) 
        ) & self.output

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
                        'value': 10,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['input_n', 'gnd']
                }
        }]
    
    def test_load(self):
        load = super().test_load()

        return load + [{
                'name': 'RLC',
                'mods': {
                    'series': ['R']
                },
                'args': {
                    'R_series': {
                        'value': 1000,
                        'unit': {
                            'name': 'ohm',
                            'suffix': 'Ω'
                        }
                    }
                },
                'pins': {
                    'input': ['output'],
                    'output': ['output_n', 'gnd']
                }
        }]
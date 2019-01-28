from bem import Block, Build
from skidl import Net, subcircuit


class Modificator(Block):
    def create_bridge(self):
        D = Build('Diode').block
    
        circuit = self.input & D()['A,K'] & self.output

    def circuit(self, **kwargs):
        super().circuit(**kwargs)

        self.output_n = self.input_n = self.gnd

    def test_sources(self):
        return super().test_sources()
        
    def test_load(self):
        load = super().test_load()

        return load + [{
                'name': 'RLC',
                'mods': {
                    'series': 'R'
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
                    'output': ['gnd']
                }
        }]
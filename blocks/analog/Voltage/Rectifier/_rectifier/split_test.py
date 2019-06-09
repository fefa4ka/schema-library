from bem.tester import Test

class Case(Test):
    def body_kit(self):
        return [{
                'name': 'basic.Resistor',
                'args': {
                    'value': {
                        'value': 1000,
                        'unit': {
                            'name': 'ohm',
                            'suffix': 'Ω'
                        }
                    }
                },
                'pins': {
                    'input': ['output_inverse'],
                    'output': ['gnd']
                }
        }]
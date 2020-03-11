from bem.tester import Test

class Case(Test):
    def body_kit(self):
        return [{
                'name': 'basic.source.VS',
                'mods': {
                    'flow': ['SINEV']
                },
                'args': {
                    'V': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 500000,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'input': ['input'],
                    'output': ['input_n']
                }
        }, {
                'name': 'basic.RLC',
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

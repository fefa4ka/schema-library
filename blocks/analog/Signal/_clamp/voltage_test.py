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
                    'value': 12,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'frequency': {
                    'value': 60,
                    'unit': {
                        'name': 'herz',
                        'suffix': 'Hz'
                    }
                }
            },
            'pins': {
                'input': ['input'],
                'output': ['gnd']
            }
        }, {
            'name'{: 'basic.source.VS',
            'mods': {
                'flow': ['V']
            },
            'args': {
                'value': {
                    'value': 3,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                }
            },
            'pins': {
                'p': ['v_ref'],
                'n': ['gnd']
            }}
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
                'output': ['output_n']
            }
        }]
   
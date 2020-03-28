from bem.tester import Test

class Case(Test):
    def body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['V'],
            },
            'args': {
                'V': {
                    'value': 10,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                }
            },
            'pins': {
                'output': ['gnd'],
                'input': ['v_ref']
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
                            'suffix': 'Ohm'
                        }
                    }
                },
                'pins': {
                    'input': ['output'],
                    'output': ['gnd']
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
                            'suffix': 'Ohm'
                        }
                    }
                },
                'pins': {
                    'input': ['output_n'],
                    'output': ['gnd']
                }
        }]
 

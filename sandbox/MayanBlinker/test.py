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
                    'value': 3.4,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                }
            },
            'pins': {
                'input': ['v_ref'],
                'output': ['gnd']
            }
        }, {
                'name': 'basic.RLC',
                'mods': {
                    'series': ['R']
                },
                'args': {
                    'R_series': {
                        'value': 500,
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
                        'value': 500,
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
 
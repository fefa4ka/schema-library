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
                        'value': 5,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 5,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 120,
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
                        'value': 10000,
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

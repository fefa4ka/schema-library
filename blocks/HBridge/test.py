from bem.tester import Test

class Case(Test):
    def sources(self):
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
            'name': 'PULSEV_2',
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
                },
                'delay_time': {
                    'value': 0.01,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                }
            },
            'pins': {
                'p': ['input_n'],
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
    
    def load(self):
        return [{
                'name': 'RLC',
                'mods': {
                    'series': ['L']
                },
                'args': {
                    'L_series': {
                        'value': 100,
                        'unit': {
                            'name': 'henry',
                            'suffix': 'H'
                        }
                    }
                },
                'pins': {
                    'input': ['output'],
                    'output': ['output_n']
                }
        }]
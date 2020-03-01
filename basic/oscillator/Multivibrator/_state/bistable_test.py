from bem.tester import Test

class Case(Test):
    def body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['PULSEV'],
            },
            'args': {
                'V': {
                    'value': 5,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'initial_value': {
                    'value': 0.1,
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
                'input': ['input'],
                'output': ['gnd']
            }
        }, {
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['PULSEV'],
            },
            'args': {
                'V': {
                    'value': 5,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'initial_value': {
                    'value': 0.1,
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
                'input': ['input_n'],
                'output': ['gnd']
            }
        }, {
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['V'],
            },
            'args': {
                'V': {
                    'value': 5,
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
 
from bem.tester import Test

class Case(Test):
    def sources(self):
        return [{
                'name': 'AMV',
                'args': {
                    'amplitude': {
                        'value': 0.2,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 1,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'carrier_frequency': {
                        'value': 3200,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    },
                    'signal_delay': {
                        'value': 0.000001,
                        'unit': {
                            'name': 'second',
                            'suffix': 's'
                        }
                    },
                    'modulating_frequency': {
                        'value': 1000000,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }, {
                'name': 'V',
                'args': {
                    'value': {
                        'value': 20,
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
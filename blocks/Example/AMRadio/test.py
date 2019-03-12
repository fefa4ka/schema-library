from bem.tester import Test

class Case(Test):
    def sources(self):
        return [{
            'name': 'AMV',
            'args': {
                'amplitude': {
                    'value': 2,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'offset': {
                    'value': 6,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'signal_delay': {
                    'value': 0.0000000001,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                },
                'carrier_frequency': {
                    'value': 5000,
                    'unit': {
                        'name': 'herz',
                        'suffix': 'Hz'
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
                'n':  ['gnd']
            }
        }]
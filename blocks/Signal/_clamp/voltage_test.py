from bem.tester import Test

class Case(Test):
    def sources(self):
        return super().test_sources() + [{
                'name': 'V',
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
                }
        }]

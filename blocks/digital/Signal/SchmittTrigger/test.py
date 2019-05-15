from bem.tester import Test

class Case(Test):
    def sources(self):
        return super().sources() + [{
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
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
                    'value': 15,
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
        }]

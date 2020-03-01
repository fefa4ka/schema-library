from bem.tester import Test

class Case(Test):
    def body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['V']
            },
            'args': {
                'V': {
                    'value': 6.5,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                }
            },
            'pins': {
                'input': ['input'],
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
                        'suffix': 'Ω'
                    }
                }
            },
            'pins': {
                'input': ['output'],
                'output': ['gnd']
            }
        }]
   
    def conditions(self, probes):
        block = self.block
        V_input = (probes['V_input'] @ u_V).canonise()
        V_output = (probes['V_output'] @ u_V).canonise()

        if V_input >= block.V_out and is_tolerated(V_output, block.V_out) == False:
            return 'V_out should be near %s, but %s' % (str(block.V_out), str(V_output))
        
         
from bem.tester import Test
from bem.simulator import Simulate
from collections import defaultdict
from bem import u

class Case(Test):
    def dc_source(self):
        return [{
                'name': 'V',
                'args': {
                    'value': {
                        'value': 5,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }]
    
    def VoltAmpereByTemperature(self, args, temperature=None):
        self._sources = self.dc_source()
        self.circuit(args)
        
        simulations = Simulate(self.block).dc({ 'VV': slice(-2, 5, .01) })
        self._sources = None
        
        
        chart = defaultdict(dict)
        for temp, simulation in simulations.items():
            label = '@ %s °C' % str(temp)
            for run in simulation:
                index = run['sweep']
                chart[index]['V_input'] = index
                chart[index][label + ' I_vv'] = run['I_vv']

        sweep = list(chart.keys())

        sweep.sort()

        return {
            'x_field': 'V_input',
            'data': [chart[index] for index in sweep]
        }


        

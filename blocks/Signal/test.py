from bem.tester import Test
from bem.simulator import Simulate
from collections import defaultdict
from bem import u

class Case(Test):
    def characteristics(self, args, temperature, voltage_sweep):
        self._sources = self.dc_source()
        self.circuit(args)
        
        simulations = Simulate(self.block).dc({ 'VV': voltage_sweep })
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

        return [chart[index] for index in sweep] 


    def FrequencyResponse(self, args, temperature=None):
        """
        
        """
        
        voltage_sweep = slice(-0.3, 0.1, .01)
        data = self.characteristics(args, temperature, voltage_sweep) 

        return {
            'x': {
                'field': 'V_input',
                'label': 'Volt',
                'unit': 'V'
            },
            'y': {
                'label': 'Current',
                'unit': 'A',
                'scale': 'sqrt',
                'domain': [-1e-8, 0]
            },
            'data': data
        }


        

        

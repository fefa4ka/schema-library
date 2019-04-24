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


    def ForwardCurrentVersusForwardVoltage(self, args, temperature=None):
        """
            The voltage drop across a forward-biased diode varies only a little with the current, and is a function of temperature; this effect can be used as a temperature sensor or as a voltage reference. 
        """
        voltage_sweep = slice(0, 2, .01)
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
                'domain': [-1e-3, 1e-3]
            },
            'data': data
        }

    def ReverseCurrentVersusReverseVoltage(self, args, temperature=None):
        """
            Also, diodes' high resistance to current flowing in the reverse direction suddenly drops to a low resistance when the reverse voltage across the diode reaches a value called the breakdown voltage.
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


        

        

from bem.tester import Test
from bem.simulator import Simulate
from collections import defaultdict
from bem import u, u_A, u_Degree, u_Hz, u_MHz
from math import log

class Case(Test):
    def characteristics(self, args, temperature, voltage_sweep):
        self.body_kit = self.ac_body_kit
        self.circuit(args)
        
        simulations = Simulate(self.block).ac(start_frequency=1@u_Hz, stop_frequency=1@u_MHz, number_of_points=10,  variation='dec', temperature=temperature)
        
        # analys[temp][freq] = v_out / v_in
        chart = defaultdict(dict)
        for temp, simulation in simulations.items():
            label = '@ %s °C' % str(temp)
            for index, frequency in enumerate(simulation.frequency):
                V_in = simulation[self.block.input.name][index]
                V_out = simulation[self.block.output.name][index]
                # label += '@ %s' % str(frequency)
                # index = simulation['sweep']
                chart[index]['Frequency'] = float(frequency)
                chart[index][label + ' Gain'] = 20 * log(float(abs(V_out) / abs(V_in)), 10) if V_out and V_in else 0

        sweep = list(chart.keys())

        sweep.sort()

        return [chart[index] for index in sweep] 


    def FrequencyResponse(self, args, temperature=None):
        """
            Frequency response of circuit
        """
        voltage_sweep = slice(0, 2, .01)
        data = self.characteristics(args, temperature, voltage_sweep)

        return {
            'x': {
                'field': 'Frequency',
                'label': 'Frequency',
                'unit': 'Hz'
            },
            'y': {
                'label': 'Atennuation',
                'unit': 'dB',
                'scale': 'sqrt',
                # 'domain': [-1e-3, 1e-3]
            },
            'data': data
        }

    def ac_body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['SINEV']
            },
            'args': {
                'V': {
                    'value': 12,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'frequency': {
                    'value': 60,
                    'unit': {
                        'name': 'herz',
                        'suffix': 'Hz'
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
                }
            },
            'pins': {
                'input': ['output'],
                'output': ['gnd']
            }
        }]
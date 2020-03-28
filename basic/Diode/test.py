from bem.tester import Test
from bem.simulator import Simulate
from collections import defaultdict
from bem import u, u_A, u_Degree

class Case(Test):
    def body_kit(self):
        return super().body_kit() + [{
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

    def dc_body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['V'],
            },
            'args': {
                'V': {
                    'value': 5,
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
                }
            },
            'pins': {
                'input': ['output'],
                'output': ['gnd']
            }
        }]

    def characteristics(self, args, temperature, voltage_sweep):
        self.body_kit = self.dc_body_kit
        self.circuit(args)

        simulations = Simulate(self.block).dc({ 'VVVS_0': voltage_sweep }, temperature=temperature)

        chart = defaultdict(dict)
        for temp, simulation in simulations.items():
            label = '@ %s °C' % str(temp)
            for run in simulation:
                index = run['sweep']
                chart[index]['V_input'] = index
                chart[index]['V_output'] = run['V_output']
                chart[index][label + ' I_vvvs_0'] = run['I_vvvs_0']

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
                'domain': [-1e-12, 0]
            },
            'data': data
        }



    def LoadLineQPoint(self, args, temperature=[25] @ u_Degree):
        """
            The Q-point can be found by plotting the graph of the load line on the i-v characteristic for the diode. The intersection of the two curves represents the quiescent operating point, or Q-point, for the diode.
        """
        voltage_sweep = slice(0, self.block.V, .1)
        data = self.characteristics(args, temperature, voltage_sweep)
        data[0]['Load_Line'] = u(self.block.I_load)
        data[len(data) - 1]['Load_Line'] = 0

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
 

from bem.tester import Test
from bem.basic import Resistor
from bem.simulator import Simulate
from collections import defaultdict
from bem import u, u_A, u_Degree

class Case(Test):
    def body_kit(self):
        return [{
            'name': 'basic.source.VS',
            'mods': {
                'flow': ['PULSEV'],
            },
            'args': {
                'V': {
                    'value': 10,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'initial_value': {
                    'value': 0.1,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'pulse_width': {
                    'value': 0.01,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                },
                'period': {
                    'value': 0.02,
                    'unit': {
                        'name': 'sec',
                        'suffix': 's'
                    }
                }
            },
            'pins': {
                'input': ['input'],
                'output': ['gnd']
            }
        }, {
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
                    'input': ['v_ref'],
                    'output': ['output']
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
                'input': ['v_ref'],
                'output': ['output']
            }
        }]

    def characteristics(self, args, temperature, voltage_sweep):
        simulations = Simulate(self.block).dc({ 'VVVS_0': voltage_sweep }, temperature=temperature)
        
        chart = defaultdict(dict)
        for temp, simulation in simulations.items():
            label = '@ %s °C' % str(temp)
            for run in simulation:
                index = run['sweep']
                # chart[index]['V_input'] = run['V_input'] #index
                chart[index]['V_input'] = run['V_input']
                # chart[index][label + ' V_input'] = run[self.node(self.block.input.name)]
                chart[index][label + ' I_output'] = run['I_vvvs_1']

        sweep = list(chart.keys())

        sweep.sort()

        return [chart[index] for index in sweep] 

        
    def LoadLineQPoint(self, args, temperature=[25] @ u_Degree):
        """
            The Q-point can be found by plotting the graph of the load line on the i-v characteristic for the diode. The intersection of the two curves represents the quiescent operating point, or Q-point, for the diode.
        """
        self.body_kit = self.dc_body_kit
        # args['base'] = Resistor()(10000)
        self.circuit(args)
        
        voltage_sweep = slice(self.block.V / -2, self.block.V, .1)
        data = self.characteristics(args, temperature, voltage_sweep)
        data[0]['Load_Line'] = u(self.block.I_load)
        data[len(data) - 1]['Load_Line'] = 0 

        return {
            'x': {
                'field': 'V_input',
                'label': 'Input Voltage',
                'unit': 'V'
            },
            'y': {
                'label': 'Output',
                'unit': 'A',
                'scale': 'sqrt'
            },
            'data': data
        }
        

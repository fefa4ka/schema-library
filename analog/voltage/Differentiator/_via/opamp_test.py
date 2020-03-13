from bem.tester import Test

from bem.simulator import Simulate
from collections import defaultdict
from bem import u, u_A, u_Degree, u_Hz, u_MHz
from math import log

class Case(Test):


    def body_kit(self):
        return [{
                'name': 'basic.source.VS',
                'mods': {
                    'flow': ['PULSEV'],
                },
                'args': {
                    'initial_value': {
                        'value': -1.5,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'V': {
                        'value': 1.5,
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
                    'flow': ['V']
                },
                'args': {
                    'V': {
                        'value': 10,
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
                'name': 'basic.source.VS',
                'mods': {
                    'flow': ['V']
                },
                'args': {
                    'V': {
                        'value': -10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'input': ['v_inv'],
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

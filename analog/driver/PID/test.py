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
                    'flow': ['SINEV']
                },
                'args': {
                    'V': {
                        'value': 1,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 0,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 100,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'input': ['set'],
                    'output': ['gnd']
                }
        },  {
                'name': 'basic.source.VS',
                'mods': {
                    'flow': ['SINEV']
                },
                'args': {
                    'V': {
                        'value': 1,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 0.5,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'delay': {
                        'value': 0,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 105,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'input': ['sensor'],
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

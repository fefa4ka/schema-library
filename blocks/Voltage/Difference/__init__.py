from bem import Block, Resistor, Transistor_Bipolar, u, u_Ohm, u_V, u_A
from skidl import Net

class Base(Block):
    V_ref = 10 @ u_V
    V_gnd = -10 @ u_V

    I_quiescent = 0.000005 @ u_A

    R_c = 0 @ u_Ohm
    R_e = 0 @ u_Ohm
    R_out = 0 @ u_Ohm

    G_diff = 0
    G_cm = 0
    CMMR = 0

    def __init__(self, V_ref, V_gnd, I_quiescent):
        self.V_ref = V_ref
        self.V_gnd = V_gnd
        self.I_quiescent = I_quiescent

        self.circuit()

    def circuit(self):
        R = Resistor()

        self.input = Net()
        self.input_n = Net()
        self.output = Net()
        self.output_n = Net()
        self.gnd = Net()
        self.v_ref = Net()
        self.v_inv = Net()

        self.R_c = (u(self.V_ref) / 2 / u(self.I_quiescent)) @ u_Ohm
        self.R_e = 1000 @ u_Ohm
        self.R_out = (u(self.V_ref) / (u(self.I_quiescent) * 2)) @ u_Ohm
        re = 25 / u(self.I_quiescent)
        self.G_diff = u(self.R_c) / (2 * (re + u(self.R_e)))
        self.G_cm = -1 * u(self.R_c) / (2 * u(self.R_out) + u(self.R_e))
        self.CMMR = self.R_out / (u(self.R_e) + re)

        amplifier = Transistor_Bipolar(
            type='npn',
            common='emitter', follow='collector'
        )

        left = amplifier(
            collector=R(self.R_c),
            emitter = R(self.R_e)
        )
        right = amplifier(
            collector=R(self.R_c),
            emitter = R(self.R_e)
        )
        power = self.v_ref & left.v_ref & right.v_ref
        left_input = self.input & left & self.output_n
        right_input = self.input_n & right & self.output
        sink = left.gnd & right.gnd & R(self.R_out) & self.v_inv

        

    def test_sources(self):
        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 0.6,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 1.6,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 120,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input_n'],
                    'n': ['gnd']
                }
        },{
                'name': 'V_1',
                'args': {
                    'value': {
                        'value': 1.6,
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
        }, {
                'name': 'V_2',
                'args': {
                    'value': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_ref'],
                    'n': ['gnd']
                }
        }, {
                'name': 'V_3',
                'args': {
                    'value': {
                        'value': -10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_inv'],
                    'n': ['gnd']
                }
        }]

    # def test_load(self):
    #     return []




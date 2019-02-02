from bem import Block, Signal, Capacitor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_F, u_H, u_Hz, u_s, u_us

class Base(Block):
    frequency = 1000000 @ u_Hz
    R_out = 1000 @ u_Ohm
    C_out = 0 @ u_Ohm

    def __init__(self, frequency=None, *args, **kwargs):
        self.frequency = frequency

        self.circuit(*args, **kwargs)

    
    def circuit(self):
        self.v_ref = Net('AMRadioVref')
        self.gnd = Net()
        self.input = Net('AMRadioInput')
        self.output = Net('AMRadioOutput')

        signal = Signal(filter=['bandpass'], clamp=['rectifier'])(
            f_0 = self.frequency,
            Q = 2,
            C_gnd = 0.000001 @ u_F,
            R_out = self.R_out
        )
        signal.gnd += self.gnd

        #RC = 0.00015  # From 1 ms to 200 ms
        RC = 100 / (self.frequency.scale * self.frequency.value) @ u_s
        
        #RC= 300 @ u_us
        self.C_out = (RC.value * RC.scale) / (self.R_out.value * self.R_out.scale) @ u_F
        C_out = Capacitor()(
            value = self.C_out,
            ref = 'C_out'
        )

        circuit = self.input & signal & self.output & C_out & self.gnd

    def test_sources(self):
        return [{
                'name': 'AMV',
                'args': {
                    'amplitude': {
                        'value': 2,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 6,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'signal_delay': {
                        'value': 0.0000000001,
                        'unit': {
                            'name': 'sec',
                            'suffix': 's'
                        }
                    },
                    'carrier_frequency': {
                        'value': 5000,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    },
                    'modulating_frequency': {
                        'value': 1000000,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n':  ['gnd']
                }
        }]
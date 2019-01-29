from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ω, u_F, u_Hz, u_H
from math import pi, sqrt

class Modificator(Base):
    """**LC Bandpass Filter**

    * Paul Horowitz and Winfield Hill. "1.7.9 RC lowpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 52-53
    """

    f_0 = 1000 @ u_Hz

    R_in = 1000 @ u_Ω
    L_series = 1e-8 @ u_H
    C_series = 1e-6 @ u_F
    R_in = 1000 @ u_Ω
    Q = 2

    def __init__(self, f_0=None, Q=None, C_series=None, *arg, **kwargs):
        self.f_0 = f_0

        # if C_series and L_series:

        f_0_value = None
        if f_0:
            f_0_value = f_0.value * f_0.scale

        self.C_series = C_series
        C_series_value = C_series.scale * C_series.value
        self.R_in = Q / (2 * pi * f_0_value * C_series_value) @ u_Ω

        self.L_series = pow(1 / (2 * pi * f_0_value * sqrt(C_series_value)), 2) @ u_H
        
        super().__init__(*arg, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalTrapOutput')

        R = Build('Resistor').block
        LC = Build('RLC', series=['L', 'C']).block
        rin = R(value=self.R_in, ref='R_in')
        lc = LC(
            L_series = self.L_series,
            C_series = self.C_series
        )
        lc.output += self.gnd

        circuit = signal & rin & (self.output | lc.input)
        


    def test_sources(self):
        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 10,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 20,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }, {
                'name': 'SINEV_1',
                'args': {
                    'amplitude': {
                        'value': 4,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': 1000,
                        'unit': {
                            'name': 'herz',
                            'suffix': 'Hz'
                        }
                    }
                },
                'pins': {
                    'p': ['input'],
                    'n': ['gnd']
                }
        }]
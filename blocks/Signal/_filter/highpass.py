from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_Ω, u_F, u_Hz
from math import pi

class Modificator(Base):
    """**RC Highpass Filter**

    We’ve seen that by combining resistors with capacitors it is possible to make frequency-dependent voltage dividers, owing to the 
    frequency dependence of a capacitor’s impedance `Z_c = −j/ωC`. 
    Such circuits can have the desirable property of passing signal frequencies of interest while rejecting undesired signal frequencies.

    Engineers like to refer to the −3 dB “breakpoint” of a filter (or of any circuit that behaves like a filter). 
    In the case of the simple RC high-pass filter, the −3 dB breakpoint is given by `f_3dB = 1/2πRC`

    The impedance of a load driven by it should be much larger than `R_gnd` in order to prevent circuit loading effects 
    on the filter’s output, and the driving source should be able to drive a `R_gnd` load without significant attenuation (loss of signal amplitude)
    in order to prevent circuit loading effects by the filter on the signal source.

    * Paul Horowitz and Winfield Hill. "1.7.8 RC highpass filters" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 48-49
    """

    f_3dB = 1000 @ u_Hz

    R_load = 1000 @ u_Ω
    R_gnd = 1000 @ u_Ω
    C_series = 1e-6 @ u_F

    def __init__(self, R_load=None, f_3dB=None, *arg, **kwargs):
        self.f_3dB = f_3dB
        f_3dB_value = f_3dB.value * f_3dB.scale
        R_gnd_value = (self.R_load.value * self.R_load.scale) / 10
        self.R_load = R_load
        self.R_gnd = R_gnd_value @ u_Ω
        self.C_series = 1 / (2 * pi * R_gnd_value * f_3dB_value) @ u_F

        super().__init__(*arg, **kwargs)

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SignalHighpassOutput')
        RLC = Build('RLC', series=['C'], gnd=['R']).block
        rlc = RLC(
            C_series = self.C_series,
            R_gnd = self.R_gnd
        )

        self.output = rlc.output
        rlc.input += signal
        rlc.gnd += self.gnd


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
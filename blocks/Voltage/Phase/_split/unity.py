from bem import Block, Resistor, Voltage_Divider, Transistor_Bipolar, Capacitor, u, u_Ohm, u_V, u_A, u_F, u_Hz
from skidl import Net
from math import pi
from .. import Base

class Modificator(Base):
    """**Unity-gain phase splitter**
    
    Sometimes it is useful to generate a signal and its inverse, i.e., two signals 180◦ out of phase. That’s easy to do – just use an emitter-degenerated amplifier with a gain of −1.

    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 88-89
    """

    V_ref = 20 @ u_V
    V_in = 6 @ u_V
    f_3db = 120 @ u_Hz
    
    V_split = 0 @ u_V
    R_out = 0 @ u_Ohm
    C_in = 0 @ u_F
    I_b = 0.001 @ u_A

    def __init__(self, V_ref, V_in, f_3db, *args, **kwargs):
        self.V_ref = V_ref
        self.V_in = V_in
        self.f_3db = f_3db

        self.V_split = self.V_ref / 6
        self.R_out = (u(self.V_split) / u(self.I_b) * 100) @ u_Ohm
    
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        R = Resistor()
        stiff_voltage = Voltage_Divider(type='resistive')(
            V_in = self.V_ref,
            V_out = self.V_split + 0.6 @ u_V,
            I_out = self.I_b
        )  
        stiff_voltage.input += self.v_ref
        stiff_voltage.gnd += self.gnd
        stiff_voltage.v_ref += self.v_ref

        splitter = Transistor_Bipolar(
            type='npn',
            common='emitter',
            follow='collector'
        )(
            collector = R(self.R_out),
            emitter = R(self.R_out)
        )
        
        split = stiff_voltage & self & splitter
        self.output = Net('OutputInverse')
        self.output_n += splitter.collector
        self.output += splitter.emitter

        self.C_in = (1 / (2 * pi * self.f_3db * R.parallel_sum(R, [self.R_out * 2 , stiff_voltage.R_in, stiff_voltage.R_out]))) @ u_F
        
        # signal = Net('VoltageShiftAcInput')
        # ac_coupling = signal & Capacitor()(self.C_in) & self.input
        # self.input = signal



    def test_sources(self):
        return [{
                'name': 'SINEV',
                'args': {
                    'amplitude': {
                        'value': 2,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'offset': {
                        'value': 3,
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
                    'p': ['input'],
                    'n': ['gnd']
                }
        }, {
                'name': 'V',
                'args': {
                    'value': {
                        'value': 20,
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
        }]

    def test_load(self):
        return []
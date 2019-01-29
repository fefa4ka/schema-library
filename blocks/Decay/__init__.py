from bem import Block, Build
from settings import parts
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_A, u_s
from math import log

class Base(Block):
    # Props
    V_in = 10 @ u_V
    V_out = 5 @ u_V
    I_out = 0.5 @ u_A
    Time_to_V_out = 0.005 @ u_s

    R_in = 0 @ u_Ohm
    C_out = 0 @ u_Ohm

    def __init__(self, V_in, V_out, I_out, Time_to_V_out):
        self.V_in = V_in
        self.V_out = V_out
        self.Time_to_V_out = Time_to_V_out

        self.circuit()

    # @subcircuit
    def circuit(self):
        R_in_value = self.R_in.value * self.R_in.scale
        C_out_value = self.C_out.value * self.C_out.scale

        if not (R_in_value and C_out_value):
            self.R_in = (self.V_in / self.I_out) @ u_Ohm
            R_in_value = self.R_in.value * self.R_in.scale

        Time_to_V_out = self.Time_to_V_out.value * self.Time_to_V_out.scale
        V_in = self.V_in.value * self.V_in.scale
        V_out = self.V_out.value * self.V_out.scale
        
        if R_in_value and not C_out_value:        
            self.C_out = (Time_to_V_out / (R_in_value * log(V_in / (V_in - V_out)))) @ u_F
        
        if C_out_value and not R_in_value:
            self.R_in = (Time_to_V_out / (C_out_value * log(V_in / (V_in - V_out)))) @ u_Ohm
        
        RLC = Build('RLC', series=['R'], gnd=['C']).block
        rlc = RLC(
            R_series = self.R_in,
            C_gnd = self.C_out
        )
        
        self.input = rlc.input
        self.output = rlc.output
        self.gnd = rlc.gnd

    def test_sources(self):
        return [{
            'name': 'PULSEV',
            'description': "Pulsed voltage source",
            'args': {
                'initial_value': {
                    'value': 0.1,
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                },
                'pulsed_value': {
                    'value': 10,
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
                'p': ['input'],
                'n': ['gnd']
            }
        }]

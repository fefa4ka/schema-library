from bem import Block, Build
from settings import parts
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_F, u_s
from math import log

class Base(Block):
    # Props
    V_in = 10 @ u_V
    V_out = 6 @ u_V
    Time_to_V_out = 0.005 @ u_s

    R_in = 0 @ u_Ohm
    C_out = 0 @ u_Ohm

    def __init__(self, V_in, V_out, Time_to_V_out):
        self.V_in = V_in
        self.V_out = V_out
        self.Time_to_V_out = Time_to_V_out

        self.circuit()

    # @subcircuit
    def circuit(self):
        C = Build('Capacitor', **self.mods, **self.props).block 
        R = Build('Resistor', **self.mods, **self.props).block

        R_in_value = self.R_in.value * self.R_in.scale
        C_out_value = self.C_out.value * self.C_out.scale

        if not (R_in_value and C_out_value):
            self.R_in = 1000 @ u_Ohm
            R_in_value = self.R_in.value * self.R_in.scale

        Time_to_V_out = self.Time_to_V_out.value * self.Time_to_V_out.scale
        V_in = self.V_in.value * self.V_in.scale
        V_out = self.V_out.value * self.V_out.scale
        
        
        if R_in_value and not C_out_value:        
            self.C_out = (Time_to_V_out / (R_in_value * log(V_in / (V_in - V_out)))) @ u_F
        
        if C_out_value and not R_in_value:
            self.R_in = (Time_to_V_out / (C_out_value * log(V_in / (V_in - V_out)))) @ u_Ohm

        self.input = Net("DecayInput")
        self.output = Net("DecayOutput")

        # self.v_ref = Net()
        self.gnd = Net()

        rin = R(value = self.R_in, ref='R_in')
        cout = C(value=self.C_out).element

        cout.ref = 'C_out'

        route = self.input & rin \
                            & self.output \
                    & cout['+,-'] \
                & self.gnd
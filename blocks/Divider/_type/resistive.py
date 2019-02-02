from .. import Base
from bem import RLC
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_mA, u_ms
import numpy as np

class Modificator(Base):
    """**Two Resistor Voltage Divider**
    
    Divider implemented by two generic resitance element.
    """

    def power(self, voltage):
        return voltage * voltage / (self.R_in_value + self.R_out_value)

    def V_out_compute(self):
        return self.R_out_value * self.V_in / (self.R_in_value + self.R_out_value)
                
    # @subcircuit
    def circuit(self):
        self.input = Net('DividerIn')
        self.output = Net('DividerOut')
        self.gnd = self.input_n = self.output_n = Net()

        #R = Build('Resistor', **self.mods, **self.props).block

        # Solving system of equation 
        V_in_value = self.V_in.scale * self.V_in.value
        V_out_value = self.V_out.scale * self.V_out.value
        I_out_value = self.I_out.scale * self.I_out.value
        A = np.array([[V_out_value, V_out_value - V_in_value], [1, 1]])
        B = np.array([[0], [V_in_value / I_out_value]])
        X = np.linalg.inv(A) @ B

        self.R_in = X[0][0] @ u_Ohm
        self.R_out = X[1][0] @ u_Ohm

        #rin = R(value = self.R_in, ref='R_in') 
        #rout = R(value=self.R_out, ref='R_out')
		
        # RLC = Build('RLC', series=['R'], gnd=['R']).block
        rlc = RLC(series=['R'], gnd=['R'])(
            R_series = self.R_in,
            R_gnd = self.R_out
        )
        self.gnd = rlc.gnd
        self.input = rlc.input
        self.output = rlc.output

        #circuit = self.input & rin & self.output & rout & self.gnd

        return 'Divider'

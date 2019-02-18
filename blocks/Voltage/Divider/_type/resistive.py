from .. import Base
from bem import RLC, u, u_Ohm, u_mA, u_ms
from skidl import Net
import numpy as np

class Modificator(Base):
    """**Two Resistor Voltage Divider**
    
    Divider implemented by two generic resitance element.
    """

    R_in = 0 @ u_Ohm
    R_out = 0 @ u_Ohm

    def circuit(self):
        self.v_ref = Net()
        self.input = Net('DividerIn')
        self.output = Net('DividerOut')
        self.gnd = self.input_n = self.output_n = Net()

        A = np.array([[u(self.V_out) , u(self.V_out)  - u(self.V_in) ], [1, 1]])
        B = np.array([[0], [u(self.V_in) / u(self.I_out)]])
        X = np.linalg.inv(A) @ B

        self.R_in = X[0][0] @ u_Ohm
        self.R_out = X[1][0] @ u_Ohm

        rlc = RLC(series=['R'], gnd=['R'])(
            R_series = self.R_in,
            R_gnd = self.R_out
        )
        self.gnd = rlc.gnd
        self.input = rlc.input
        self.output = rlc.output

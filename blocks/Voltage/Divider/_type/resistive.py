from .. import Base
from bem import RLC, u, u_Ohm, u_mA, u_ms
from skidl import Net
import numpy as np

class Modificator(Base):
    """**Two Resistor Voltage Divider**
    
    Voltage dividers are often used in circuits to generate a particular voltage from a larger fixed (or varying) voltage.

    The humble voltage divider is even more useful, though, as a way of thinking about a circuit: the input voltage and upper resistance might represent the output of an amplifier, say, and the lower resistance might represent the input of the following stage. 
    
    In this case the voltage-divider equation tells you how much signal gets to the input of that last stage. This will all become clearer after you know about a remarkable fact (Thévenin’s theorem) that will be discussed later. First, though, a short aside on voltage sources and current sources.
    """

    R_in = 0 @ u_Ohm
    R_out = 0 @ u_Ohm

    def __init__(self, *args, **kwargs):
        """
            R_in -- The input voltage and upper resistance might represent the output of an amplifier
            R_out -- The lower resistance might represent the input of the following stage
        """
        super().__init__(*args, **kwargs)

    def circuit(self):
        self.v_ref = Net()
        self.input = Net('DividerIn')
        self.output = Net('DividerOut')
        self.gnd = self.input_n = self.output_n = Net()

        A = np.array([[u(self.V_out), u(self.V_out - self.V_in) ], [1, 1]])
        B = np.array([[0], [u(self.V_in / self.I_load)]])
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

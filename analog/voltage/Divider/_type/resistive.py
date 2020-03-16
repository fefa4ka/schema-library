from .. import Base
from bem import u, u_Ohm, u_mA, u_ms
from bem.basic import Resistor
from bem import Net
import numpy as np
from lcapy import R, LSection
from settings import params_tolerance


class Modificator(Base):
    """**Two Resistor Voltage Divider**

    Voltage dividers are often used in circuits to generate a particular voltage from a larger fixed (or varying) voltage.

    The humble voltage divider is even more useful, though, as a way of thinking about a circuit: the input voltage and upper resistance might represent the output of an amplifier, say, and the lower resistance might represent the input of the following stage.

    In this case the voltage-divider equation tells you how much signal gets to the input of that last stage. This will all become clearer after you know about a remarkable fact (Thévenin’s theorem) that will be discussed later. First, though, a short aside on voltage sources and current sources.
    """

    def willMount(self, R_in = 0 @ u_Ohm):
        """
            R_in -- Output impeadance that could be used as part of the divider
        """
        self.load(self.V)

        # Find right values
        A = np.array([[u(self.V_out), u(self.V_out - self.V) ], [1, 1]])
        B = np.array([[0], [u(self.V / self.I_load)]]) # + (1 * params_tolerance)))]])
        X = np.linalg.inv(A) @ B

        self.R_in = X[0][0] @ u_Ohm - self.R_in
        self.R_out = X[1][0] @ u_Ohm

    def network(self):
        return LSection(
            R('R_in'),
            R('R_out')
        )

    def circuit(self):
        """
            R_in -- The input voltage and upper resistance might represent the output of an amplifier
            R_out -- The lower resistance might represent the input of the following stage
        """
        if self.R_in > 0 @ u_Ohm:
            input = self.input & Resistor()(self.R_in) & self.output
        else:
            self.input & self.output
        output = self.output & Resistor()(self.R_out) & self.gnd

        self.Power = self.R_in + self.R_out
        self.consumption(self.V)

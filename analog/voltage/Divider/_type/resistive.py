from .. import Base
from bem import u, u_Ohm, u_mA, u_ms
from bem.basic import Resistor
from bem import Net
import numpy as np
from lcapy import R, LSection
from settings import params_tolerance


class Modificator(Base):
    """## Two Resistor Voltage Divider
    The humble voltage divider is even more useful, though, as a way of thinking about a circuit: the input voltage and upper resistance might represent the output of an amplifier, say, and the lower resistance might represent the input of the following stage.

    In this case the voltage-divider equation tells you how much signal gets to the input of that last stage.

    `V_(out) / V_(in) = R_(out) / (R_(in) + R_(out))`

    What is `V_(out)`? Well, the current (same everywhere, assuming no “load” on the output; i.e., nothing connected across the output) is: `I = V / (R_(in) + R_(out))`
    `V_(out) = I * R_(out) = (R_(out) / (R_(in) + R_(out))) * V`

    * Paul Horowitz and Winfield Hill. "1.2.3 Voltage Dividers" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 7-8

    """
    props = { 
        'R_in': 0 @ u_Ohm,
        'R_out': 0 @ u_Ohm
    }

    def willMount(self,):
        """
            R_in -- The input voltage and upper resistance might represent the output of an amplifier
            R_out -- The lower resistance might represent the input of the following stage
        """
        self.load(self.V_out)

        # Find right values
        A = np.array([[u(self.V_out), u(self.V_out - self.V) ], [1, 1]])
        B = np.array([[0], [u(self.V / (self.I_load * 5))]]) # + (1 * params_tolerance)))]])
        X = np.linalg.inv(A) @ B

        self.R_in = X[0][0] @ u_Ohm - self.props.get('R_in', 0 @ u_Ohm)
        self.R_out = X[1][0] @ u_Ohm - self.props.get('R_out', 0 @ u_Ohm)

        self.I_in = self
    def network(self):
        return LSection(
            R('R_in'),
            R('R_out')
        )

    def circuit(self):
        R = Resistor()
        if self.R_in > 0 @ u_Ohm:
            input_load = R.parallel_sum(R, [self.R_out, self.R_load])
            input = R(self.R_in, Load=input_load)
            self.input & input & self.output
            self.V_out = self.V - input.V_drop
        else:
            self.input & self.output

        if self.R_out > 0 @ u_Ohm:
            output = Resistor()(self.R_out, V=self.V_out)
            self.output & output & self.gnd
        else:
            self.output & self.gnd

        self.Power = self.R_in + self.R_out
        self.consumption(self.V)

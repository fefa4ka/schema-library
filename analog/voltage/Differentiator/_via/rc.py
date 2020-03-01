from math import log

from PySpice.Unit import u_A, u_F, u_Ohm, u_s, u_V, u_Hz
from .. import Base
from bem import u
from bem.basic import RLC


class Modificator(Base):
    """**Simple RC Differentiator**
    
    `V_(out)(t) = RC * (d/dt) * V_(in)(t)`

    * Paul Horowitz and Winfield Hill. "1.4.3 Differetiators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 25
    """


    frequency = 50 @ u_Hz
    C_in = 0 @ u_F
    R_out = 0 @ u_Ohm

    def willMount(self, frequency):
        self.load(self.V)

    # @subcircuit
    def circuit(self):
        period = 1 / u(self.frequency)
        quant = period / 4
        rate = u(self.V) / quant
        
        self.RC = u(self.V) / rate

        if not (self.C_in and self.R_out):
            self.R_out = (self.V / self.I_load) @ u_Ohm

        if not self.R_out:
            self.R_out = (self.RC / u(self.C_out)) @ u_Ohm

        if not self.C_in:        
            self.C_in = (self.RC / u(self.R_out)) @ u_F
        
        rlc = RLC(series=['C'], gnd=['R'])(
            C_series = self.C_in,
            R_gnd = self.R_out
        )
        
        self.input = self.v_ref = rlc.input
        self.output = rlc.output
        self.gnd = rlc.gnd

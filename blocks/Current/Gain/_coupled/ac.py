from .. import Base
from bem import Resistor, Capacitor, u, u_F, u_Hz
from skidl import Net
from math import pi


class Modificator(Base):
    """**For AC-Coupled signal**
 
    """
    f_3db = 120 @ u_Hz

    C_in = 0 @ u_F
    C_out = 0 @ u_F

    def __init__(self, f_3db, *arg, **kwarg):
        """
        C_in -- `C_(i\\n) = 1 / (2 pi f_(3db)R_(i\\n))`
        C_out -- `C_(out) = 1 / (2 pi f_(3db)R_(load))` 
        """
        self.f_3db = f_3db

        super().__init__(*arg, **kwarg)

    def circuit(self):
        super().circuit()
        
        self.C_in = (1 / (2 * pi * self.f_3db * self.R_in)) @ u_F
        self.C_out = (1 / ((2 * pi * self.f_3db) * (self.R_e + self.R_load))) @ u_F
        signal = self.input
        self.input = Net('ACGainInput')
        ac_input = self.input & Capacitor()(self.C_in) & signal
        
        output = self.output
        self.output = Net('ACGainOutput')
        ac_output = output & Capacitor()(self.C_out) & self.output

from bem import Block, RLC, u, u_Ohm, u_V, u_A, u_F, u_Hz
from skidl import Net
from math import pi
from .. import Base

class Modificator(Base):
    """**Phase shifter**

    A nice use of the phase splitter.  This circuit gives (for a sinewave input) an output sinewave of adjustable phase (from zero to 180◦) and with constant amplitude.

    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 89
    """

    V_in = 6 @ u_V
    angle = 0
    f_3db = 120 @ u_Hz

    R_shift_out = 500000 @ u_Ohm
    C_shift_in = 0.000001 @ u_F
    

    def __init__(self, C_shift_in, R_shift_out, *args, **kwargs):
        self.C_shift_in = C_shift_in
        self.R_shift_out = R_shift_out
        
        super().__init__(*args, **kwargs)

    def circuit(self):
        super().circuit()
        
        shifter = RLC(series=['C'], gnd=['R'])(
            C_series = self.C_shift_in,
            R_gnd = self.R_shift_out
        )

        shifter.input += self.output_n
        shifter.gnd += self.output

        self.output = Net('ShiftedSignal')
        self.output += shifter.output
        self.output_n = Net()

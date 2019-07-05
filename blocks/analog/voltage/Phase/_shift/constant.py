from bem.basic import RLC
from bem import Net, u, u_Ohm, u_V, u_A, u_F, u_Hz
from math import pi, atan, tan
from .. import Base

class Modificator(Base):
    """**Phase shifter**

    A nice use of the phase splitter.  This circuit gives (for a sinewave input) an output sinewave of adjustable phase (from zero to 180◦) and with constant amplitude.

    * Paul Horowitz and Winfield Hill. "2.2.7 Common-emitter amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 89
    """

    V = 6 @ u_V
    angle = 45
    f_3db = 100 @ u_Hz

    R_shift_out = 1000000 @ u_Ohm
    C_shift_in = 0 @ u_F
    

    def willMount(self, angle, R_shift_out=None):
        """
            angle -- Phase shift angle `theta = 2 tan^-1 omega RC`
        """
        
        angle_rad = pi / (180 / self.angle)
        atan_desire = angle_rad / 2
        atan_argument = tan(atan_desire)
        angular_speed = 2 * pi * self.f_3db
        RC = atan_desire / angular_speed
        
        self.C_shift_in = (RC / self.R_shift_out) @ u_F
        self.C_shift_in = self.C_shift_in.canonise()

        self.angle = 2 * atan(2 * pi * self.f_3db * self.C_shift_in * self.R_shift_out) * 180 / pi

    def circuit(self):
        super().circuit()
        
        shifter = RLC(series=['C'], gnd=['R'])(
            C_series = self.C_shift_in,
            R_gnd = self.R_shift_out,
            **self.load_args
        )

        shifter.input += self.output_n
        shifter.gnd += self.output

        self.output = Net('ShiftedSignal')
        self.output += shifter.output
        self.output_n = None

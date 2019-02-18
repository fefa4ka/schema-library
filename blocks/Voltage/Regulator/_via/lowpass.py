from .. import Base
from bem import Signal, u_Hz
from skidl import Net, subcircuit

class Modificator(Base):
    """**Eliminate the effect of ripple current**

    A nice variation of this circuit aims to eliminate the effect of ripple current (through `R`) on the zener voltage by supplying the zener current from a current source, which is the subject of §2.2.6. An alternative method uses a lowpass filter in the zener bias circuit. `R` is chosen such that the series pair provides sufficient zener current. Then `C` is chosen large enough so that `RC ≫ 1/ f_ripple`.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 83
    """

    F_ripple = 120 @ u_Hz
    def __init__(self, F_ripple, *args, **kwargs):
        self.F_ripple = F_ripple

        super().__init__(*args, **kwargs)

    def circuit(self):
        self.R_load /= 2

        super().circuit()
        
        reduce_ripple = Signal(filter=['lowpass'])(
            input=self.input,
            R_load = self.R_load,
            f_3dB = self.F_ripple
        )

        reduce_ripple.input += self.input
        reduce_ripple.gnd += self.gnd

        self.input = reduce_ripple.output
        

        
        # self.R_protect = self.R_load / 10
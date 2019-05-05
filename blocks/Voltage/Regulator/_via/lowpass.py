from .. import Base
from bem import Signal, u_Hz
from skidl import Net, subcircuit

class Modificator(Base):
    """**Eliminate the effect of ripple current**

    A nice variation of this circuit aims to eliminate the effect of ripple current (through `R`) on the zener voltage by supplying the zener current from a current source, which is the subject of §2.2.6. An alternative method uses a lowpass filter in the zener bias circuit. `R` is chosen such that the series pair provides sufficient zener current. Then `C` is chosen large enough so that `RC ≫ 1/ f_(rippl\e)`.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 83
    """

    frequency = 120 @ u_Hz
    def willMount(self, frequency):
        """
            frequency -- Input signal frequency
        """
        pass

    def circuit(self):

        super().circuit()
        
        reduce_ripple = Signal(filter=['lowpass'])(
            input=self.input,
            f_3dB = self.frequency,
            V = self.V,
            Load=self.R_load / 2,
        )

        reduce_ripple.input += self.input
        reduce_ripple.gnd += self.gnd

        self.input = reduce_ripple.output
        
from .. import Base
from bem.basic import Resistor
from bem.basic.transistor import Bipolar

from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Base):
    """## Emittor Follower as Voltage Regilator

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83
    """

    def circuit(self):
        super().circuit()

        """
        The collector resistor  can be added to protect the transistor from momentary output
        short circuits by limiting the current, even though it is not essential to the emitter follower
        function.

        Choose value so that the voltage drop across it is less than the drop across resistor for the highest
        normal load current (i.e., so that the transistor does not saturate at maximum load).
        """
        protect = Resistor()(self.R_load * 5)
        """
        By using an emitter follower to isolate the zener, you get the improved circuit.

        Zener current can be made relatively independent
        of load current, since the transistor base current is small, and far lower zener power
        dissipation is possible (reduced by as much as a factor of `β`).
        """
        follower = Bipolar(type='npn', follow='emitter')(
            base = protect
        )

        follower.input & self.output
        follower.v_ref & self.input
        self.output = follower.output



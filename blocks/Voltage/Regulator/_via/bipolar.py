from .. import Base
from bem import Transistor_Bipolar, Resistor
from skidl import Net, subcircuit
from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Base):
    """**Emittor Follower as Voltage Regilator**

    By using an emitter follower to isolate the zener, you get the improved circuit. Now the situation is much better. Zener current can be made relatively independent of load current, since the transistor base current is small, and far lower zener power dissipation is possible (reduced by as much as a factor of `β`). The collector resistor `RC` can be added to protect the transistor from momentary output short circuits by limiting the current, even though it is not essential to the emitter follower function. Choose `RC` so that the voltage drop across it is less than the drop across `R` for the highest normal load current (i.e., so that the transistor does not saturate at maximum load).

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83
    """

    R_protect = 0 @ u_Ohm
    def circuit(self):
        super().circuit()

        self.R_protect = self.R_load / 10
        
        follower = Transistor_Bipolar(type='npn', follow='emitter')(
            base=Resistor()(self.R_protect)
        )

        follower.input += self.output
        follower.v_ref += self.v_ref
        self.output = follower.output

        


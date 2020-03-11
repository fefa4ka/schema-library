from bem import u, u_A, u_Ohm, u_V
from bem.analog.voltage import Divider
from bem.basic import Diode, Resistor
from skidl import Net

from .. import Base

class Modificator(Base):
    """**Diode Voltage Clamp**

    Sometimes it is desirable to limit the range of a signal (i.e., prevent it from exceeding certain voltage limits) somewhere in a circuit.

    A voltage divider can provide the reference voltage for a clamp. In this case you must ensure that the resistance looking into the voltage divider (`I_out`) is small compared with `R_load`.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    """

    def willMount(self, V_ref=10 @ u_V, V_out=3 @ u_V, I_ref=0.01 @ u_A):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('SignalClampedOutput')

        Rref = None
        if self.V_out and self.V_ref and self.V_ref >  self.V_out:
            Rref = Divider(type='resistive')(
                V = self.V_ref,
                V_out = self.V_out,
                Load=self.I_ref)
            Rref.gnd += self.gnd
        else:
            Rref = Resistor()(667)

        clamp = self.v_ref & Rref & Diode(type='generic')(V=self.V_ref, Load=self.Load)['K', 'A'] & self.output
        signal_input = signal & Resistor()(self.R_load) & self.output

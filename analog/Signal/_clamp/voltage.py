from bem import u, u_A, u_Ohm, u_V
from bem.analog.voltage import Divider
from bem.basic import Diode, Resistor
from skidl import Net


class Modificator:
    """## Diode Voltage Clamp

    Sometimes it is desirable to limit the range of a signal (i.e., prevent it from exceeding certain voltage limits) somewhere in a circuit.

    A voltage divider can provide the reference voltage for a clamp. In this case you must ensure that the resistance looking into the voltage divider (`I_out`) is small compared with `R_load`.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    """

    def willMount(self, V_out=3 @ u_V):
        self.load(V_out)

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('SignalClampedOutput')

        Rref = None
        clamp = Diode(type='generic')()
        if self.V_out and self.V and self.V > self.V_out:
            Rref = Divider(type='resistive')(
                V = self.V,
                V_out = self.V_out - clamp.V_j,
                Load=self.I_load * 10)
            Rref.gnd += self.gnd
        else:
            Rref = Resistor()(667)

        self.v_ref & Rref & clamp['K', 'A'] & self.output
        signal_input = signal & Resistor()(self.R_load / 3) & self.output

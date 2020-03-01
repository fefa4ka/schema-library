from .. import Base
from bem import Net, u_Hz
from bem.basic import Diode, Resistor
from bem.analog import Filter

class Modificator(Base):
    """**Compensating Diode Forward Voltage Drop**

    A possible circuit solution to this problem of finite diode drop. Here D1 compensates D2’s forward drop by providing 0.6 V of bias
    to hold D2 at the threshold of conduction. Using a diode (D1) to provide the bias (rather than, say, a voltage divider) has severalo
    advantages: (a) there is nothing to adjust, (b) the compensation will be nearly perfect, and (c) changes of the forward drop (e.g., with changing temperature) will be compensated properly.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    * Review of block https://electronics.stackexchange.com/questions/68019/compensating-the-forward-voltage-drop-of-a-diode-signal-rectifier
    """

    f_3dB = 1000 @ u_Hz

    def willMount(self, f_3dB):
        self.load(self.V)
        self.R_stiff = self.R_load

    def circuit(self):
        super().circuit()

        R = Resistor()
        D = Diode(type='generic')

        signal = self.input
        self.input = Net('CompensationInput')
        ref_point = Net('CompensationDropVref')

        """
        Only a small positive upswing from the input is required to bring it to conduction. Because the input is capacitively coupled,
        it is pure AC. Its swings are additively superimposed on top of the bias voltage that exists on the other side of the capacitor.
        The 5V source is just from somewhere in the rest of the circuit. There is nothing special about it.
        """
        ac_coupling = Filter(highpass='rc')(V=self.V, f_3dB_high=self.f_3dB, Load=self.R_stiff)
        self.input & ac_coupling & signal

        """
        The 𝑅1, 𝑅3 and 𝐷1 circuit basically creates a 0.6V bias on the other side of the capacitor, so that a positive swing
        in the signal does not have to overcome a 0.6V hurdle. 𝐷1 and 𝑅3 form a shunt voltage regulator.
        """
        voltage_regulator = ref_point & R(self.R_stiff) & self.v_ref

        """
        The purpose of R1 is to act as a flexible linkage to separate the reference 0.6 voltage, which is quite stiff,
        from the point where the signal is injected, which must on the contrary be free to swing about 0.6V.

        R1 also protects the diode from the input current swings. If we replace R1 by a wire, it won't work because
        the signal will try to move the voltage at the top of D1, whose cathode is pinned to ground.
        The input's positive swings will dump current through D1, abusing it. That creates a poor input impedance,
        resulting in an inability to generate the right voltage on or under D2.

        On the other hand, if R1 is made large, the compensation diminishes, because the reference
        voltage is able to exert less control over the bias.
        """
        compensator = ac_coupling.gnd & ref_point & D() & self.gnd

        """
        A negative swing of 0.1V turns to 0.5V. But this cannot create a -0.1V output at the bottom of D2; that is nonsense
        because it is outside of our supply range. 0.5V is not enough to forward bias D2, and so the output is at 0V,
        pulled to ground by R2, which has almost no current flowing across it to create any voltage.
        """
        after_pull = self.output & R(self.R_stiff * 10) & self.gnd

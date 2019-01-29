from .. import Base, Build
from skidl import Net, subcircuit
from PySpice.Unit import u_pF, u_Ohm

class Modificator(Base):
    """**Signal Rectifier**

    There are other occasions when you use a diode to make a waveform of one polarity only. If the input waveform isn’t a sinewave, you usually don’t think of it as a recti- fication in the sense of a power supply. For instance, you might want a train of pulses corresponding to the rising edge of a square wave. The easiest way is to rectify the dif- ferentiated wave (Figure 1.69). Always keep in mind the 0.6 V(approximately) forward drop of the diode. This cir- cuit, for instance, gives no output for square waves smaller than 0.6 V pp. If this is a problem, there are various tricks to circumvent this limitation. One possibility is to use hot carrier diodes (Schottky diodes), with a forward drop of about 0.25 V.
    """

    R_out = 1000 @ u_Ohm

    def __init__(self, R_out=None, *args, **kwargs):
        self.R_out = R_out

        super().__init__(*args, **kwargs)

    def circuit(self, *args, **kwargs):
        super().circuit(*args, **kwargs)

        D = Build('Diode').block
        R = Build('Resistor').block

        signal = self.output
        self.output = Net('SignalRecrifierOutput')

        circuit = signal & D()['A,K'] & self.output & R(value=self.R_out) & self.gnd

        # compensationVoltageDropDiode = D()
        # compensation = signal & R(value=self.R_out) & compensationVoltageDropDiode.input & R(value=self.R_out) & (self.v_ref)
        # compensationVoltageDropDiode.output += self.gnd
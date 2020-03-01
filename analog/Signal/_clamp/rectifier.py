from .. import Base
from skidl import Net 
from bem.basic import Resistor, Diode, Capacitor
from bem.analog.voltage import Differentiator, Rectifier

from PySpice.Unit import u_pF, u_Ohm, u_Hz

class Modificator(Base):
    """**Signal Rectifier**

    There are other occasions when you use a diode to make a waveform of one polarity only. If the input waveform isn’t a sinewave, you usually don’t think of it as a rectification in the sense of a power supply. For instance, you might want a train of pulses corresponding to the rising edge of a square wave. The easiest way is to rectify the dif ferentiated wave (Figure 1.69). Always keep in mind the 0.6 V(approximately) forward drop of the diode. This circuit, for instance, gives no output for square waves smaller than 0.6 V pp. If this is a problem, there are various tricks to circumvent this limitation. One possibility is to use hot carrier diodes (Schottky diodes), with a forward drop of about 0.25 V.

    * Paul Horowitz and Winfield Hill. "1.6.6 Circuit applications of diodes" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 35-36
    """
    frequency = 50 @ u_Hz

    def willMount(self, frequency):
        pass

    def circuit(self, *args, **kwargs):
        super().circuit(*args, **kwargs)

        output = Net('SignalRecrifiedOutput')
        rectifier = self & \
            Differentiator(via='rc')(V=self.V, Load=self.Load, frequency=self.frequency) & \
                Rectifier(wave='half')(V=self.V, Load=self.Load, frequency=self.frequency) & \
                    output

        self.output = output

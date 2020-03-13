from bem.abstract import Electrical
from bem.basic import OpAmp, Resistor
from bem.basic.transistor import Bipolar
from bem import u_Hz
from math import pi, sqrt


class Base(Electrical()):
    """
        This design is used to buffer signals by presenting a high input impedance and a low output impedance.
        This circuit is commonly used to drive low-impedance loads, analog-to-digital converters (ADC) and buffer
        reference voltages. The output voltage of this circuit is equal to the input voltage.

        * http://www.ti.com/lit/an/sboa269a/sboa269a.pdf
    """
    props = {
        'via': ['opamp', 'bipolar', 'mosfet']
    }

    def willMount(self, Frequency=100 @ u_Hz):
        """
            V -- Verify that the amplifier can achieve the desired output swing using the supply voltages provided
            V_signal -- Signal amplitude
            slew_rate -- The rate of change in the output voltage caused by a step change on the input.
        """
        self.load(self.V)
        self.V_signal = self.V / sqrt(2) # RMS
        self.slew_rate = 2 * pi * self.Frequency * self.V

    def circuit(self):
        via = self.props.get('via', None)
        buffer = None

        if via == 'opamp':
            """
            1. Use the op-amp linear output operating range, which is usually specified under the AOL test conditions.
            2. The small-signal bandwidth is determined by the unity-gain bandwidth of the amplifier.
            3. Check the maximum output voltage swing versus frequency graph in the datasheet to minimize slewinduced distortion.
            4. The common mode voltage is equal to the input signal.
            5. Do not place capacitive loads directly on the output that are greater than the values recommended in
            the datasheet.
            6. High output current amplifiers may be required if driving low impedance loads
            """
            buffer = OpAmp()(frequency=self.Frequency)
            buffer.input_n & buffer.output & self.output

        if via == 'bipolar':
            buffer = Bipolar(type='npn', emitter='follower')()
            buffer & self.output

        if buffer:
            self.input & buffer

            buffer.v_ref & self.v_ref
            buffer.gnd & self.gnd
        else:
            self.input & self.output

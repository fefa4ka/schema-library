from .. import Base


class Modificator(Base):
    """
        This design is used to buffer signals by presenting a high input impedance and a low output impedance.
        This circuit is commonly used to drive low-impedance loads, analog-to-digital converters (ADC) and buffer
        reference voltages. The output voltage of this circuit is equal to the input voltage.

        1. Use the op-amp linear output operating range, which is usually specified under the AOL test conditions.
        2. The small-signal bandwidth is determined by the unity-gain bandwidth of the amplifier.
        3. Check the maximum output voltage swing versus frequency graph in the datasheet to minimize slewinduced distortion.
        4. The common mode voltage is equal to the input signal.
        5. Do not place capacitive loads directly on the output that are greater than the values recommended in
        the datasheet.
        6. High output current amplifiers may be required if driving low impedance loads

        * http://www.ti.com/lit/an/sboa269a/sboa269a.pdf
    """

    def circuit(self):
        super().circuit()
        self.input_n & self.output

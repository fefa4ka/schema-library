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


        ```
        # Power Supply
        signal = VS(flow='SINEV')(V=2.5, frequency=100)

        # Signal
        v_ref = VS(flow='V')(V=10)

        load = Resistor()(1000)

        # Amplifier
        buffer = Example() 

        # Network
        v_ref & buffer.v_ref
        signal & buffer.input
        buffer & load & buffer.v_inv & signal.gnd & v_ref


        watch = buffer
        ```
        * http://www.ti.com/lit/an/sboa269a/sboa269a.pdf
    """

    def circuit(self):
        super().circuit()
        self.input_n & self.output

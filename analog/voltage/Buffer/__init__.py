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

        ```
        # Power Supply
        v_ref = VS(flow='V')(V=10)
        v_inv = VS(flow='V')(V=-10)

        # Signal
        signal = VS(flow='SINEV')(V=0.7, frequency=100)

        load = Resistor()(1000)

        # Amplifier
        buffer = Example() 

        # Network
        v_ref & buffer.v_ref
        v_inv & buffer.gnd
        signal & buffer.input
        buffer & load & signal.gnd & v_ref


        watch = buffer
        ```

        * http://www.ti.com/lit/an/sboa269a/sboa269a.pdf
    """
    props = {
        'via': ['opamp', 'bipolar']
    }

    def willMount(self, Frequency=100 @ u_Hz):
        """
            V -- Verify that the amplifier can achieve the desired output swing using the supply voltages provided
            V_signal -- Signal amplitude
            slew_rate -- The rate of change in the output voltage caused by a step change on the input
        """
        self.load(self.V)
        self.V_signal = self.V / sqrt(2) # RMS
        self.slew_rate = 2 * pi * self.Frequency * self.V

    def circuit(self):
        via = self.props.get('via', [None])
        buff = None

        if 'opamp' in via:
            """
            1. Use the op-amp linear output operating range, which is usually specified under the AOL test conditions.
            2. The small-signal bandwidth is determined by the unity-gain bandwidth of the amplifier.
            3. Check the maximum output voltage swing versus frequency graph in the datasheet to minimize slewinduced distortion.
            4. The common mode voltage is equal to the input signal.
            5. Do not place capacitive loads directly on the output that are greater than the values recommended in
            the datasheet.
            6. High output current amplifiers may be required if driving low impedance loads
            """
            buff = OpAmp()(Frequency=self.Frequency)
            buff.input_n & buff.output & self.output

        if 'bipolar' in via:
            buff = Bipolar(type='npn', emitter='follower')(Frequency=self.Frequency)
            buff & self.output

        if buff:
            self.input & buff

            buff.v_ref & self.v_ref

            gnd = buff.gnd
            if hasattr(buff, 'v_inv'):
                gnd = buff.v_inv
            gnd & self.gnd
        else:
            self.input & self.output

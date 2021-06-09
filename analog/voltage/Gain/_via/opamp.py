from bem.abstract import Electrical
from bem.analog import Filter
from bem.basic import OpAmp, Resistor
from bem import u_Hz, Net
from math import pi

class Modificator(Electrical()):
    """
        This design amplifies the input signal, `V`, with a signal gain of `Gain`. The input signal may come 
        from a high-impedance source (for example, MΩ) because the input impedance of this circuit is determined by
        the extremely high input impedance of the op amp (for example, GΩ). The common-mode voltage of a
        non-inverting amplifier is equal to the input signal.

       ```
        # Power Supply
        v_ref = VS(flow='V')(V=10)
        v_inv = VS(flow='V')(V=-10)

        # Signal
        signal = VS(flow='SINEV')(V=0.7, frequency=1e4)

        load = Resistor()(1000)

        # Amplifier
        buffer = Example()

        # Network
        v_ref & buffer.v_ref
        v_inv & buffer.v_inv
        signal & buffer.input
        buffer & load & signal.gnd & buffer.gnd & v_ref


        watch = buffer
        ```

    """

    pins = {
        'input': True, # The input impedance of this circuit is equal to the input impedance of the amplifier.
        'output': True, # Avoid placing capacitive loads directly on the output of the amplifier to minimize stability issues
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, Gain=2, Frequency=1e4 @ u_Hz):
        # Calculate the minimum slew rate required to minimize slew-induced distortion
        self.Slew_rate = 2 * pi * self.V * Frequency

    def circuit(self):
        R = Resistor()

        amplifier = OpAmp()(Frequency=self.Frequency)
        self.v_ref & amplifier.v_ref
        self.v_inv & amplifier.v_inv

        # Using high-value resistors can degrade the phase margin of the circuit and introduce additional noise in the circuit.
        feedback = R(self.R_load * 10) # Common principle to use much larger input impeadance compared to load before amplifier TODO: Why?
        source = R(feedback.value / (self.Gain - 1))

        if self.Frequency:
            pre_filter = Filter(highpass='rc')(
                f_3dB_high = self.Frequency,
                Load = self.I_load / 100
            )
            pre_filter.gnd & self.gnd

            ac_input = Net("AcCoupledInput")
            ac_input & pre_filter & amplifier.input
            self.input = ac_input
        else:
            self.input & amplifier.input

        self.gnd & amplifier.gnd & source & amplifier.input_n & feedback & amplifier.output & self.output

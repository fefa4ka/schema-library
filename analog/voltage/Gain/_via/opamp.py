from bem.abstract import Electrical
from bem.basic import OpAmp, Resistor
from bem import u_Hz
from math import pi

class Modificator(Electrical()):
    """
        This design amplifies the input signal, `V`, with a signal gain of `Gain`. The input signal may come 
        from a high-impedance source (for example, MΩ) because the input impedance of this circuit is determined by
        the extremely high input impedance of the op amp (for example, GΩ). The common-mode voltage of a
        non-inverting amplifier is equal to the input signal.
    """

    pins = {
        'input': True, # The input impedance of this circuit is equal to the input impedance of the amplifier.
        'output': True, # Avoid placing capacitive loads directly on the output of the amplifier to minimize stability issues
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, Gain=2, Frequency=1e3 @ u_Hz):
        # Calculate the minimum slew rate required to minimize slew-induced distortion
        self.Slew_rate = 2 * pi * self.V * Frequency

    def circuit(self):
        R = Resistor()

        amplifier = OpAmp()(frequency=self.Frequency)
        self.v_ref & amplifier.v_ref
        self.v_inv & amplifier.gnd

        # Using high-value resistors can degrade the phase margin of the circuit and introduce additional noise in the circuit.
        feedback = R(self.R_load * 10) # Common principle to use much larger input impeadance compared to load before amplifier TODO: Why?
        source = R(feedback.value / (self.Gain - 1))

        self.input & amplifier.input
        self.gnd & source & amplifier.input_n & feedback & amplifier.output & self.output

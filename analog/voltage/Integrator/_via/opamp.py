from bem.abstract import Electrical
from bem.basic import Resistor, Capacitor, OpAmp
from bem.analog.voltage import Divider
from bem import u_Hz, u_Ohm, u_kOhm, u_F
from math import pi

class Modificator(Electrical()):
    """
        The integrator circuit outputs the integral of the input signal over a frequency range based on the circuit
        time constant and the bandwidth of the amplifier. The input signal is applied to the inverting input so the
        output is inverted relative to the polarity of the input signal. The ideal integrator circuit will saturate to the
        supply rails depending on the polarity of the input offset voltage and requires the addition of a feedback
        resistor, R_feedback, to provide a stable DC operating point. The feedback resistor limits the lower frequency range
        over which the integration function is performed. This circuit is most commonly used as part of a larger
        feedback/servo loop which provides the DC feedback path, thus removing the requirement for a feedback
        resistor.

        * http://www.ti.com/lit/an/sboa275a/sboa275a.pdf
    """

    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, Q=100, Frequency=1e3 @ u_Hz):
        pass

    def circuit(self):
        """
            C_integrator -- `C_(integrator) = 1 / (2 * pi * R_(in) * f_(0db))`
        """
        R = Resistor()

        # Set R_input to a standard value
        sensor = R(100 @ u_kOhm)
        # Calculate C_integrator to set the unety-gain integration frequency.
        integrator = Capacitor()((1 / (2 * pi * sensor.value * self.Frequency)) @ u_F)
        # Calculate R_feedback to set the lower cutoff frequency a decade less than the minimum operating frequency
        feedback = R((10  / (2 * pi * integrator.value * self.Frequency / self.Q)) @ u_Ohm)

        self.H = -1 / (sensor.value * integrator.value)

        # Select an amplifier with a gain bandwidth at least 10 times the desired maximum operating frequency
        buffer = OpAmp()(frequency=self.Frequency * self.Q)

        buffer.v_ref & self.v_ref
        buffer.gnd & self.v_inv

        self.input & sensor & buffer.input_n & (feedback | integrator) & buffer.output & self.output
        self.gnd & buffer.input

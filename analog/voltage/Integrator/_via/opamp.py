from bem.abstract import Electrical
from bem.basic import Resistor, Capacitor, OpAmp
from bem.analog.voltage import Divider
from bem import u_Hz, u_Ohm, u_kOhm, u_F
from math import pi

class Modificator(Electrical()):
    """
    ## OpAmp Integrator
    The integrator circuit outputs the integral of the input signal over a frequency range based on the circuit
    time constant and the bandwidth of the amplifier. The input signal is applied to the inverting input so the
    output is inverted relative to the polarity of the input signal.

    The ideal integrator circuit will saturate to the supply rails depending on the polarity of the input offset
    voltage and requires the addition of a feedback resistor, R_feedback, to provide a stable DC operating point.
    The feedback resistor limits the lower frequency range over which the integration function is performed.

    ```
    # Power supply
    v_ref = VS(flow='V')(V=10)
    v_inv = VS(flow='V')(V=-10)

    signal = VS(flow='PULSEV')(V=3, Frequency=1e3)
    load = Resistor()(1000)

    # Amplifier
    integrator = Example()

    # Network
    v_ref & integrator.v_ref
    v_inv & integrator.v_inv

    signal & integrator.input

    integrator.output & load & v_ref

    integrator.gnd & v_inv.gnd & v_ref.gnd & signal.gnd

    watch = integrator
    ```



    This circuit is most commonly used as part of a larger feedback/servo loop which provides the DC feedback path,
    thus removing the requirement for a feedback resistor.

    * http://www.ti.com/lit/an/sboa275a/sboa275a.pdf
    """

    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, Q=10, Frequency=1e3 @ u_Hz):
        pass

    def circuit(self):
        """
            C_integrator -- `(integrator) = 1 / (2 * pi * (sensor) * (Frequency))`
        """
        R = Resistor()

        # Set R_input to a standard value
        sensor = R(100 @ u_kOhm)
        # Calculate C_integrator to set the unity-gain integration frequency
        integrator = Capacitor()((1 / (2 * pi * sensor.value * self.Frequency)) @ u_F)
        # Calculate R_feedback to set the lower cutoff frequency a decade less than the minimum operating frequency
        feedback = R((10  / (2 * pi * integrator.value * self.Frequency * self.Q)) @ u_Ohm)

        self.H = -1 / (sensor.value * integrator.value)

        # Select an amplifier with a gain bandwidth at least 10 times the desired maximum operating frequency
        buffer = OpAmp()(Frequency=self.Frequency * self.Q)
        buffer.connect_power_bus(self)

        self.input & sensor & buffer.input_n & (feedback | integrator) & buffer.output & self.output
        self.gnd & buffer.input

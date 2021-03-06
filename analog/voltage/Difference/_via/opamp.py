from .. import Base
from skidl import Net
from bem.basic import Resistor, OpAmp
from bem import Net, u, u_Ohm, u_V, u_A, u_kOhm

class Modificator(Base):
    """
        ## OpAmp Based
        This design inputs two signals, `\input` and `\input_n`, and outputs their difference (subtracts). The input signals
        typically come from low-impedance sources because the input impedance of this circuit is determined by
        the resistive network. Difference amplifiers are typically used to amplify differential input signals and reject
        common-mode voltages. A common-mode voltage is the voltage common to both inputs. The
        effectiveness of the ability of a difference amplifier to reject a common-mode signal is known as commonmode rejection ratio (CMRR). The CMRR of a difference amplifier is dominated by the tolerance of the
        resistors.
    """
    pins = {
        'input': 'InputA',
        'output': True,
        'input_n': 'InputB',
        'output_n': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, gain=10):
        self.load(self.V)
        # The input impedance is determined by the input resistive network. Make sure these values are large
        # when compared to the output impedance of the sources.
        self.R_in = self.R_load * 10
        self.R_feedback = self.R_in * gain

    def circuit(self):
        R = Resistor()
        diff = self.props.get('unit', None)
        if not diff:
            diff = OpAmp()(V=self.V)

        input_p = self.input & R(self.R_in) & diff.input
        input_n = self.input_n & R(self.R_in) & diff.input_n

        sense = diff.input_n & R(self.R_feedback) & diff.output
        ref = diff.input & R(self.R_feedback) & self.gnd

        self.v_ref += diff.v_ref
        self.v_inv += diff.v_inv

        self.output += diff.output
		
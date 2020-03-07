from skidl import Net

from bem import u_V, u_Hz, u_Ohm, u_s, u_kOhm
from bem.abstract import Network, Virtual
from bem.analog import Signal
from bem.analog.voltage import Decay
from bem.basic import Resistor
from bem.basic.transistor import Bipolar

from .. import Base


class Modificator(Base):
    """
    A bistable multivibrator is a circuit that is designed to remain in either of two states indefinitely until a control signal is applied that causes it to change states. After the circuit switches states, another signal is required to switch it back to its previous state. To understand how this circuit works, initially assume that V1 = 0V. This means that the transistor Q2 has no base current and hence no collector current. Therefore, current that flows through R4 and R3 flows into the base of transistor Q1, driving it into saturation. In the saturation state, V1 = 0, as assumed initially. Now, because the circuit is symmetric, you can say it is equally stable with V2 = 0 and Q1 saturated. The bistable multivibrator can be made to switch from one state to another by simply grounding either V1 or V2 as needed. This is accomplished with switch S1. Bistable multivibrators can be used as memory devices or as frequency dividers, since alternate pulses restore the circuit to its initial state.”

    * Paul Scherz. “Practical Electronics for Inventors, Fourth Edition
    * https://www.electronics-tutorials.ws/waveforms/monostable.html
    """

    pins = {
        'v_ref': True,
        'input': 'Trigger',
        'output': True,
        'gnd': True
    }

    width = 0.03 @ u_s
    frequency = 50 @ u_Hz

    def willMount(self, frequency, width):
        pass

    def circuit(self):
        R = Resistor()
        Gate = Bipolar(type='npn', follow='collector', common='emitter')

        rectifier = Signal(clamp='rectifier')(V = self.V, Load = self.Load, frequency = self.frequency)

        trigger = Gate(
            collector=R(self.R_load, ref='Trigger_Collector'),
            base=R(self.R_load * 10, ref='Trigger_Base'))

        pulse = Gate(
            collector=lambda T: Resistor()((self.V - (T['VCE'] or 0.3) @ u_V) / self.I_load, ref='Pulse_Collector')
        )
        delay = Decay()(
            V = self.V,
            V_out = self.V / 2,
            Time_to_V_out = self.width,
            Load = (self.V - trigger.V_je) / (3 * self.I_load / pulse.Beta),
            reverse = True
        )

        self.v_ref & trigger.v_ref & pulse.v_ref
        self.gnd & trigger.gnd & pulse.gnd & rectifier.gnd

        self.input & rectifier & trigger.base

        pulse & trigger & delay.gnd
        self.v_ref & delay & pulse & self.output


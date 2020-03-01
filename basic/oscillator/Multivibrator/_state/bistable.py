from .. import Base
from bem.abstract import Network
from bem import u_Ohm
from bem.basic import Resistor
from bem.basic.transistor import Bipolar

class Modificator(Base, Network(port='two')):
    """
    A bistable multivibrator is a circuit that is designed to remain in either of two states indefinitely until a control signal is applied that causes it to change states. After the circuit switches states, another signal is required to switch it back to its previous state. To understand how this circuit works, initially assume that V1 = 0V. This means that the transistor Q2 has no base current and hence no collector current. Therefore, current that flows through R4 and R3 flows into the base of transistor Q1, driving it into saturation. In the saturation state, V1 = 0, as assumed initially. Now, because the circuit is symmetric, you can say it is equally stable with V2 = 0 and Q1 saturated. The bistable multivibrator can be made to switch from one state to another by simply grounding either V1 or V2 as needed. This is accomplished with switch S1. Bistable multivibrators can be used as memory devices or as frequency dividers, since alternate pulses restore the circuit to its initial state.”

    Excerpt From: Paul Scherz. “Practical Electronics for Inventors, Fourth Edition”. Apple Books. 
    """

    pins = {
        'v_ref': True,
        'gnd': True,
        'input': 'Set',
        'input_n': 'Reset',
        'output': True,
        'output_n': True
    }

    def circuit(self):
        def State():
            return Bipolar(type='npn', follow='collector', common='emitter')(
                base=Resistor()(self.R_load * 10, ref='R_in'),
                collector=Resistor()(self.R_load, ref='R_collector')
            )

        set = State()
        reset = State()
 
        bistable = self & set & reset & set

        self.input += set.base
        self.input_n += reset.base

        self.output = set.output
        self.output_n = reset.output
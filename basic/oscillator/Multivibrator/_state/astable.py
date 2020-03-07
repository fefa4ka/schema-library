from .. import Base
from bem.abstract import Network
from bem import u_V, u_Ohm, u_s
from bem.basic import Resistor, Diode
from bem.analog.voltage import Decay
from bem.basic.transistor import Bipolar
from bem.digital.signal import SchmittTrigger

class Modificator(Base):
    """
    An asatable multivibrator is a circuit that is not stable in either of two possible output states and it acts like an oscillator. It also requires no external trigger pulse, but uses positive feedback network and a RC timer network to create built-in triggering that switches the output between VCC and 0V. The result is a square wave frequency generator. In the circuit to the left, Q1 and Q2 are switching transistors connected in cross-coupled feedback network, along with two time-delay capacitors. The transistors are biased for linear operation and are operated as common emitter amplifiers with 100% positive feedback. When Q1 is OFF, its collector voltage rises toward VCC, while Q2 if ON. As this occurs, plate A of capacitor C1 rises towards VCC. Capacitor C1’s other plate B, which is connected to the base of Q2 is at 0.6V since Q2 is in conducting state, thus the voltage across C1 is 6.0 − 0.6V = 5.4V. (It’s high value of charge). The instant Q1 switches ON, plate A of C1 falls to 0.6V, causing an equal and instantaneous fall in voltage on plate B of C1. C1 is pulled down to −5.4 (reverse charge) and[…]

    * Excerpt From: Paul Scherz. “Practical Electronics for Inventors, Fourth Edition”. Apple Books. 
    * https://electrosome.com/astable-multivibrator-transistors/
    """

    pins = {
        'v_ref': True,
        'gnd': True,
        'input': True,
        'output': True,
        'output_n': True
    }

    set_period = 0.5 @ u_s
    reset_period = 0.3 @ u_s
    V_load = 5 @ u_V

    def willMount(self, set_period, reset_period):
        self.load(self.V)

        self.duty_cycle = reset_period / (reset_period + set_period)

    def circuit(self):
        Gate = Bipolar(type='npn', follow='collector', common='emitter')
        R = Resistor()
        D = Diode(type='generic')

        def Oscillator(controller, width):
            # R1 & R2 should be chosen such that it should give the required collector current during saturation state.
            # Min. Base Current, Ibmin = Ic / β, where β is the hFE of the transistor
            # Safe Base Current,Ib = 10 * Ibmin = 3 x Ic / β
            return Decay()(
                V = self.V,
                V_out = self.V * 0.5,
                Time_to_V_out = width,
                Load = (self.V - controller.V_je) / (3 * self.I_load / controller.Beta) * 10, # * 10 because in Decay Load / 10
                reverse = True
            )

        def State():
            return Gate(
                # The resistance R should be designed to limit the collector current Ic with in a safe limit.
                # In normal cases, V = (Vcc – Vce) 
                collector = lambda T: R((self.V - (T['VCE'] or 0.3) @ u_V) / self.I_load)
            )

        def Sharp(state, oscillator):
            oscillator.gnd & R(self.R_load) & self.v_ref

            return state & oscillator.gnd & D(V=self.V, Load=self.Load)

        set = State()
        set_oscillator = Oscillator(set, self.set_period)

        reset = State()
        reset_oscillator = Oscillator(reset, self.reset_period)

        self.v_ref & reset_oscillator.input & set_oscillator.input & set.v_ref & reset.v_ref

        Sharp(set, set_oscillator) & self.output
        Sharp(reset, reset_oscillator) & self.output_n

        set_oscillator & reset.input
        reset_oscillator & set.input

        self.gnd & set.gnd & reset.gnd

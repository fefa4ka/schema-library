from bem.basic import Resistor
from bem import Net, u_Ohm, u_A, u_V
from bem.analog.voltage import Divider
from bem.basic.transistor import Bipolar
from .. import Base


class Modificator(Base):
    """
    * http://www.johnhearfield.com/Eng/Schmitt.htm
    """

    def circuit(self):
        Gate = Bipolar(type='npn', foloow='collector', common='emitter')
        R = Resistor()

        # Next, choose the current that will flow in T2. A low value saves energy but implies a high value of collector load resistor, which might slow down the switching edges. 
        # Choose self.I_load mA in T_on for now.
        R_E = R(self.V_on / self.I_load)

        R_on = R((self.V - self.V_on) / self.I_load)

        # Finally, choose T_off's collector current and hence the lower threshold voltage VN. 
        # The noise spikes look troublesome, so it would be sensible to aim for around V_on - V_off - which would give about V_histeresis of hysteresis
        self.V_histeresis = self.V_on - self.V_off

        # It follows that the designer must ensure that the current in T_off (I1) is smaller than the current in T_on (I2), or the circuit won't work!
        I_off = self.V_off / R_E.value
        R_off = R((self.V - self.V_off) / I_off)

        # R_limit limits T_off's maximum base current, which could safely be I_off / 30 (because the transistor won't have a current gain lower than 30)
        I_limit = I_off / 30 # Amplifier Gain

        # I'm assuming that the circuit is driven from a zero-impedance voltage source. If it's not, then the source impedance can be subtracted from R_limit.
        R_limit = R((self.V - self.V_off) / I_limit)

        off = Gate(
            base = R_limit,
            collector = R_off,
            emitter = R_E
        )

        on = Gate(
            collector = R_on
        )

        # The two resistors form a potential divider which must set T_on's base at (say) V_base with T_off off,
        # and draw a current significantly higher than T_on's base current, which can't exceed [I_load / 30] = I_on
        # Choose the bleed current through RA & RB to be about I_bleed = I_on * 5, so that it's much larger than T_on's base current.
        I_bleed = self.I_load / 6
        V_base = self.V_on + off.V_je

        bleed = Divider(type='resistive')(
            V = self.V,
            V_out = V_base,
            Load = I_bleed,
            R_in = R_off.value
        )

        off & bleed
        bleed.output & on.base
        on.emitter & off.emitter

        self.v_ref & on.v_ref & off.v_ref
        self.gnd & off.gnd

        self.input & off
        on & self.output


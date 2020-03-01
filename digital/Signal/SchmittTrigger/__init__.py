from bem.basic import Resistor
from bem import Net, u_Ohm, u_A
from bem.abstract import Electrical
from bem.analog.voltage import Difference, Divider
from bem.basic.transistor import Bipolar

class Base(Electrical()):
    """**Schmitt Trigger**
    TODO: Relaxation Oscillator https://en.wikipedia.org/wiki/Schmitt_trigger
    """

    def circuit(self):
        self.load(self.V)
        amplifier = Difference(via='bipolar')(
            V = self.V,
            Load = self.Load,
            V_ref = self.V / 2,
            V_gnd = self.V / -2,
            I_quiescent = 0.0001 @ u_A
        )

        split_power = Divider(type='resistive')(
            V = self.V, 
            V_out = self.V / 2,
            Load = self.R_load / 2
        )

        # threshold = Divider(type='resistive')(
        #     V = self.V, 
        #     V_out = self.V / 1.5,
        #     Load = self.Load / amplifier.CMMR
        # )

        split_power.input += self.v_ref, amplifier.v_ref
        split_power.output += self.gnd#, threshold.gnd
        split_power.gnd += amplifier.v_inv

        
        self.input & Resistor()(self.R_load * amplifier.CMMR) & amplifier
        amplifier.output_n & amplifier.input_n

        self.output += amplifier.output
    
        
        # self.v_ref += amplifier.v_ref
        # self.gnd += amplifier.v_inv#, threshold.gnd
        # self.output += amplifier.output
        # self.input += amplifier.input_n
        # self.output += 

        # & amplifier.input_n

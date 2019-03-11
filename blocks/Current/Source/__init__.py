
from bem import Block, Voltage_Divider, Transistor_Bipolar, Resistor, u, u_ms, u_Ohm, u_A, u_V, u
from skidl import Net, subcircuit
from settings import params_tolerance
from random import randint

class Base(Block):
    """**Transistor Current Source**
    
    Happily, it is possible to make a very good current source with a transistor. It works like this: applying `V_b` to the base, with `V_b>0.6 V`, ensures that the emitter is always conducting:

    `V_e = V_b − 0.6 V`
    so
    `I_e = V_e / R_e = (V_b − 0.6 V) / R_e`

    But, since `I_e ≈ I_(load)` for large beta,
    `I_(load) ≈ (V_b − 0.6 V) / R_e`

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 86

    """

    V_ref = 10 @ u_V

    V_b = 0 @ u_V
    Load = 0.01 @ u_A
    R_e = 0 @ u_Ohm

    def __init__(self, V_ref, Load):
        """
        V_je -- Base-emitter built-in potential
        
        """
        self.V_ref = V_ref
        self.Load = Load
        self.load(self.V_ref)

        self.circuit()

    def circuit(self, **kwargs):
        self.input = Net()
        self.output_n = Net()
        self.output = Net()
        self.v_ref = Net()
        self.gnd = Net()

        generator = Transistor_Bipolar(type='npn', follow='emitter')()
        # self.Beta = generator.selected_part.spice_params['BF']
        self.V_je = (generator.selected_part.spice_params.get('VJE', None) or 0.6) @ u_V

        self.V_e = (u(self.V_je) + randint(1, int(u(self.V_ref) / 2))) @ u_V
        self.V_b = self.V_e + self.V_je
        self.R_e = self.V_e / self.I_load

        generator.collector += self.output_n
    
        
        controller = Voltage_Divider(type='resistive')(
            V_in = self.V_ref,
            V_out = self.V_b,
            Load = self.I_load
        )
    
        controller.input += self.v_ref
        controller.gnd += self.gnd

        source = controller.output & generator & Resistor()(self.R_e) & self.gnd

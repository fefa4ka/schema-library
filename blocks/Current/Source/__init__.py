
from bem import Block, Voltage_Divider, Transistor_Bipolar, Resistor, u, u_ms, u_Ohm, u_A, u_V, u
from skidl import Net, subcircuit
from settings import params_tolerance
from random import randint

class Base(Block):
    """**Transistor Current Source**
    
    Happily, it is possible to make a very good current source with a transistor (Figure 2.31). It works like this: applying VB to the base, with VB>0.6 V, ensures that the emitter is always conducting:

    `V_e = V_b − 0.6 volts`
    
    so

    `I_e = V_e / R_e = (V_b − 0.6 volts) / R_e`

    But, since `I_e ≈ I_c` for large beta,
    
    `I_c ≈ (V_b − 0.6 volts) / R_e`

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 86

    """

    V_ref = 25 @ u_V
    I_out = 0.01 @ u_A

    V_b = 0 @ u_V

    I_control = 0 @ u_A
    R_e = 0 @ u_Ohm
    load = None

    def __init__(self, V_ref, I_out):
        self.V_ref = V_ref
        self.I_out = I_out
        # self.load = load or Resistor()(10000)

        self.circuit()

    def circuit(self, **kwargs):
        self.input = Net()
        self.output_n = Net()
        self.output = Net()
        self.v_ref = Net()
        self.gnd = Net()
        
        Diode_drop = 0.6 @ u_V
        self.V_e = (u(Diode_drop) + randint(1, int(u(self.V_ref) / 2))) @ u_V
        self.V_b = self.V_e + Diode_drop
        self.R_e = (u(self.V_e) / u(self.I_out)) @ u_Ohm

        generator = Transistor_Bipolar(type='npn', follow='emitter')()
        Beta = generator.selected_part.spice_params['BF']

        generator.collector += self.output_n
        
        self.I_control = (u(self.I_out) / Beta) @ u_A
        
        controller = Voltage_Divider(type='resistive')(
            V_in = self.V_ref,
            V_out = self.V_b,
            I_out = self.I_control
        )
    
        controller.input += self.v_ref
        controller.gnd += self.gnd

        source = controller.output & generator & Resistor()(self.R_e) & self.gnd

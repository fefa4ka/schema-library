from bem import Block, Build, Diode, Resistor
from bem import u, u_s, u_ms, u_Ohm, u_A, u_V
from bem import is_tolerated
from skidl import Net, subcircuit
from settings import params_tolerance



class Base(Block):
    """**Voltage Regulator**
    
    The simplest regulated supply of voltage is simply a zener. Some current must flow through the zener.

    * Paul Horowitz and Winfield Hill. "2.2.4 Emitter followers as voltage regulators" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 82-83

    """

    V_in = 25 @ u_V
    V_out = 10 @ u_V
    I_out = 0.01 @ u_A

    R_load = 0 @ u_Ohm

    def __init__(self, V_in=None, V_out=None, I_out=None):
        self.V_in = V_in
        self.V_out = V_out
        self.I_out = I_out

        self.R_load = (
            (u(self.V_in) - u(self.V_out))
            / (u(self.I_out) * (1 + params_tolerance))
        ) @ u_Ohm

        self.circuit()
    
    def circuit(self, **kwargs):
        self.input = Net("VoltageRegulatorInput")
        self.gnd = Net()
        self.v_ref = self.input
        
        # self.input_n = Net()
        self.output = Net("VoltageRegulatorOutput")

        regulator = self.input & Resistor()(self.R_load) & self.output & Diode(type='zener', BV=u(self.V_out))()['K, A'] & self.gnd


    def test_sources(self):
        sources = super().test_sources()[:]
        sources[0]['args']['amplitude']['value'] = 25

        return sources

    def test_cases(self, probes):
        V_input = (probes['V_input'] @ u_V).canonise()
        V_output = (probes['V_output'] @ u_V).canonise()

        if V_input >= self.V_out and is_tolerated(V_output, self.V_out) == False:
            return 'V_out should be near %s, but %s' % (str(self.V_out), str(V_output))
        
        
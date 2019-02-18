from bem import Block, u_Ohm, u, u_V, u_A
from skidl import Net
from settings import params_tolerance

class Base(Block):
    """**Voltage Manipulator**

    """

    # Props
    V_in = 10 @ u_V
    V_out = 3 @ u_V
    I_out = 0.06 @ u_A

    R_load = 0 @ u_Ohm

    def __init__(self, V_in, V_out, I_out):
        self.V_in = V_in
        self.V_out = V_out
        self.I_out = I_out

        self.R_load = (
            (u(self.V_in) - u(self.V_out))
            / (u(self.I_out) * (1 + params_tolerance))
        ) @ u_Ohm

        self.circuit()

    def circuit(self):
        self.input = self.output = Net("VoltageInput")
        self.gnd = self.input_n = self.output_n = Net()
        self.v_ref = Net()
        
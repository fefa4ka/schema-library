from bem.abstract import Electrical, Network
from bem.basic import Resistor, RLC
from skidl import Part, Net, TEMPLATE, subcircuit
from PySpice.Unit import u_V, u_H, u_Ohm

class Base(Electrical(), Network(port='two')):
    """
    """
    increase = False

    V = 25 @ u_V
    V_out = 10 @ u_V
    coupling_factor = 0.9
    turns_ration = 5


    def willMount(self, V_out, coupling_factor, turns_ration):
        self.load(self.V_out)

    #  def __series__(self, instance):
    #     if self.output and instance.input:
    #         self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
    #         self.output += instance.input

    #     if self.output_gnd and instance.gnd:
    #         self.output_gnd += instance.gnd

    #     if self.v_ref and instance.v_ref:
    #         self.v_ref += instance.v_ref

    def part_spice(self):
        from skidl.pyspice import K

        Transformer = {
            '1': Net('TransformerInputP'),
            '2': Net('TransformerInputN'),
            '3': Net('TransformerOutputP'),
            '4': Net('TransformerOutputN')
        }

        Spacer = Resistor()(value=1 @ u_Ohm)
        # Lin = L(value=100 @ u_H)
        Lin = RLC(series=['L', 'R'])(
            R_series = 1 @ u_Ohm,
            L_series = 10 @ u_H
        )
        Lout = RLC(series=['L', 'R'])(
            R_series = 1 @ u_Ohm,
            L_series = .5 @ u_H
        )
        primary = Transformer['1'] & Lin & Transformer['2']
        secondary = Transformer['3'] & Lout & Transformer['4']

        transformer = K(inductor1='L_s', inductor2='L_s_1', coupling_factor=self.coupling_factor)

        return Transformer

    def circuit(self, *args, **kwargs):
        transformer = self.part_spice() if self.SIMULATION else self.part()

        self.v_ref = Net()
        self.gnd = Net()

        self.input = transformer['1']
        self.input_n = transformer['2']

        self.output = transformer['3']
        self.output_n = transformer['4']

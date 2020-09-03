from PySpice.Unit import u_H, u_Hz, u_Ohm, u_V, u_Wb
from skidl import TEMPLATE, Net, Part, subcircuit

from bem import u
from bem.abstract import Network, Physical
from bem.basic import RLC, Resistor

from math import pi, sqrt


class Base(Network(port='two'), Physical()):
    """
    # Transformer
    ## (No implemented)

    If we want the primary coil to produce a stronger magnetic
    field to overcome the cores magnetic losses, we can either
    send a larger current through the coil, or keep the same current
    flowing, and instead increase the number of coil turns (`N_p`) of the winding.


    ```
    vs = VS(flow='SINEV')(V=5, frequency=[1e3, 1e6])
    load = Resistor()(1000)
    transformer = Example()
    vs.output & transformer.input
    vs.output_n & transformer.input_n


    transformer.output & load & transformer.output_n


    watch = inductor
    ```

    """

    def willMount(self, V=25 @ u_V, V_out=10 @ u_V, Frequency = 220 @ u_Hz, Windings=2, Coupling_factor=0.9 @ u_Wb):
        """
        V -- The Primary Voltage
        V_out -- The Secondary Voltage
        Windings -- The number of coil windings
        turns_ratio -- `V / V_(out) = N_p / N_s = n`
        Coupling_factor -- The Flux Linkage, the amount of flux in webers
        At -- The product of amperes times turns is called the “ampere-turns”, which determines the magnetising force of the coil.
        """
        self.turns_ratio = u(self.V / self.V_out)
        self.N_p = 100
        angle_speed = 2 * pi * self.Frequency
        self.EMF_max = self.Windings * angle_speed * Coupling_factor
        self.EMF_rms = ((2 * pi) / sqrt(2)) * self.Windings * Coupling_factor * self.Frequency
        self.At = self.I * self.N_p
        self.load(self.V_out)

    #  def __series__(self, instance):
    #     if self.output and instance.input:
    #         self.output._name = instance.input._name = f'{self.name}{instance.name}_Net'
    #         self.output += instance.input

    #     if self.output_gnd and instance.gnd:
    #         self.output_gnd += instance.gnd

    #     if self.v_ref and instance.v_ref:
    #         self.v_ref += instance.v_ref

    def part_spice(self, *args, **kargs):
        from skidl.pyspice import K

        Transformer = {
            '1': Net('TransformerInputP'),
            '2': Net('TransformerInputN'),
            '3': Net('TransformerOutputP'),
            '4': Net('TransformerOutputN')
        }

        Spacer = Resistor()(value=1 @ u_Ohm)
        Lin = L(value=100 @ u_H)
        #Lin = RLC(series=['L', 'R'])(
        #    R_series = 1 @ u_Ohm,
        #    L_series = 10 @ u_H
        #)
        #Lout = RLC(series=['L', 'R'])(
        #    R_series = 1 @ u_Ohm,
        #    L_series = .5 @ u_H
        #)
        primary = Transformer['1'] & Lin & Transformer['2']
        secondary = Transformer['3'] & Lout & Transformer['4']

        # Hack: should be hardcoded ref for inductors
        # Probably skidl or PySpice bug
        transformer = K(inductor1='L_s', inductor2='L_s_1', coupling_factor=u(self.Coupling_factor))

        return Transformer

    def circuit(self, *args, **kwargs):
        transformer = self.part()

        self.v_ref = Net()
        self.gnd = Net()

        self.input = transformer['1']
        self.input_n = transformer['2']

        self.output = transformer['3']
        self.output_n = transformer['4']

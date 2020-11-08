from PySpice.Unit import u_H, u_Hz, u_Ohm, u_V, u_Wb
from skidl import TEMPLATE, Net, Part, subcircuit

from bem import Build, u, u_Ω, u_H, u_pF, u_mH
from bem.abstract import Network, Physical, Virtual
from bem.basic import RLC, Resistor, Capacitor, Inductor

from math import pi, sqrt


class Base(Network(port='two'), Physical()):
    """
    # Transformer

    If we want the primary coil to produce a stronger magnetic
    field to overcome the cores magnetic losses, we can either
    send a larger current through the coil, or keep the same current
    flowing, and instead increase the number of coil turns (`N_p`) of the winding.


    ```
    vs = VS(flow='SINEV')(V=220, frequency=60)
    load = Resistor()(1000)
    transformer = Example()
    vs.output & transformer.input
    vs.gnd & transformer.input_n


    transformer.output & load & transformer.output_n


    watch = transformer
    ```

    """

    def willMount(self, V=220 @ u_V, V_out=10 @ u_V, Frequency = 60 @ u_Hz, Windings=2, Coupling_factor=0.99 @ u_Wb):
        """
        V -- The Primary Voltage
        V_out -- The Secondary Voltage
        Windings -- The number of coil windings
        turn_ratio -- `V / V_(out) = N_p / N_s = n`
        Coupling_factor -- The Flux Linkage, the amount of flux in webers
        At -- The product of amperes times turns is called the “ampere-turns”, which determines the magnetising force of the coil.
        """
        self.turn_ratio = u(self.V / self.V_out)
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
    def part_spice(self,
                 primary_inductance=1@u_H,
                 copper_resistance=1@u_Ω,
                 leakage_inductance=1@u_mH,
                 winding_capacitance=20@u_pF,
                 **kwargs
             ):

        C = Capacitor(virtual_part=True)
        R = Resistor(virtual_part=True)
        L = Inductor(virtual_part=True)

        pins = {
            'input': ('input', ['1']),
            'input_n': ('input_n', ['2']),
            'output': ('output', ['3']),
            'output_n': ('output_n', ['4'])
        }
        Transformer = Virtual()(
            pins=pins,
            input=Net('TransformerInputP'), 
            input_n=Net('TransformerInputN'), 
            output=Net('TransformerOutputP'), 
            output_n=Net('TransformerOutputN')
        )

        # For an ideal transformer you can reduce the values for the flux leakage inductances, the
        # copper resistors and the winding capacitances. But
        if copper_resistance <= 0:
            raise ValueError("copper resistance must be > 0")
        if leakage_inductance <= 0:
            raise ValueError("leakage inductance must be > 0")
        secondary_inductance = primary_inductance / float(self.turn_ratio**2)

        # Primary
        primary_leakage = L(value=leakage_inductance)
        primary = L(value=primary_inductance)
        primary_copper = R(value=copper_resistance)

        Transformer['1'] & primary_leakage & primary & primary_copper & Transformer['2']

        # Secondary
        secondary_leakage = L(value=leakage_inductance)
        secondary = L(value=secondary_inductance)
        secondary_copper = R(value=copper_resistance)

        Transformer['3'] & secondary_leakage & secondary & secondary_copper & Transformer['4']

        coupling = Build('K').spice(inductor1=primary.ref, inductor2=secondary.ref, coupling_factor=u(self.Coupling_factor))

        return Transformer

    def circuit(self, *args, **kwargs):
        transformer = self.element = self.part()

        self.v_ref = Net()
        self.gnd = Net()

        self.input = transformer['1']
        self.input_n = transformer['2']

        self.output = transformer['3']
        self.output_n = transformer['4']

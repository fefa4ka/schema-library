from bem import Build, u, u_Ohm, u_m, u_Hz, u_s
from bem.abstract import Physical
from math import pi
from scipy.constants import speed_of_light
from skidl import Part, TEMPLATE

class Base(Physical()):
    """**Transmittion Line**

    * Paul Scherz. "2.5.1 How the Shape of a Conductor Affects Resistance" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    """
    frequency = 1000000000 @ u_Hz
    length = 1 @ u_m
    diameter = 2.05e-3 @ u_m

    resistivity = (1.59e-8 @ u_Ohm) * (1 @ u_m)
    temperature_alpha = 0.0039

    def willMount(self, length, diameter, frequency):
        radius = (self.diameter / 2)
        self.area = pi * radius * radius
        self.Power = self.resistivity * self.length / self.area

        # Power Dissipation
        if self.Load.is_same_unit(1 @ u_Ohm):
            I_total = self.current(self.V, self.Load + self.Power)
        elif self.Load.is_same_unit(1 @ u_A):
            I_total = self.I + self.Load
        elif self.Load.is_same_unit(1 @ u_W):
            I_total = (self.P + self.Load) / self.V
        
        self.V_drop = self.Power * I_total
        
        self.load(self.V - self.V_drop)
        self.consumption(self.V_drop)

    def part_spice(self, *args, **kwargs):
        return Build('T').spice(*args, **kwargs)

    def part_template(self):
        pin_head = {
            'library': 'Connector_Generic',
            'name': 'Conn_01x04',
            'footprint': 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'
        }

        part = Part(pin_head['library'], pin_head['name'], footprint=pin_head['footprint'], dest=TEMPLATE)
        
        part.set_pin_alias('ip', 1)
        part.set_pin_alias('op', 3)

        part.set_pin_alias('in', 2)
        part.set_pin_alias('on', 4)
        
        return part

    def circuit(self):
        c = speed_of_light * (1 @ u_m) / (1 @ u_s)
        frequency = self.frequency #self.input.signal.frequency
        self.wave_length = c / frequency
        self.normalized_length = u(self.length / self.wave_length)
        
        self.element = self.part(impedance=self.Z, frequency=frequency, normalized_length=self.normalized_length)

        self.input += self.element['ip']
        self.output += self.element['op']

        self.gnd += self.element['in', 'on']

    
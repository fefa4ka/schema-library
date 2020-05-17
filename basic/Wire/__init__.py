from bem import Build, u, u_Ohm, u_m, u_Hz, u_s, u_A, u_W
from bem.abstract import Physical
from math import pi
from scipy.constants import speed_of_light
from skidl import Part, TEMPLATE

class Base(Physical()):
    """# Transmittion Line

    * Paul Scherz. "2.5.1 How the Shape of a Conductor Affects Resistance" Practical Electronics for Inventors — 4th Edition. McGraw-Hill Education, 2016
    """
    resistivity = (1.59e-8 @ u_Ohm) * (1 @ u_m)
    temperature_alpha = 0.0039

    def willMount(self, length=1 @ u_m, diameter=1.05e-3 @ u_m, frequency=1e9 @ u_Hz):
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

    def circuit(self):
        c = speed_of_light * (1 @ u_m) / (1 @ u_s)
        frequency = self.frequency #self.input.signal.frequency
        self.wave_length = c / frequency
        self.normalized_length = u(self.length / self.wave_length)

        self.element = self.part(impedance=self.Z, frequency=frequency, normalized_length=self.normalized_length)
        # ip, op -- positive line in Spice Transmmittion element
        self.input & (self.element['ip'] or self.element[1])
        self.output & (self.element['op'] or self.element[2])

        # in, on -- negative line, used for ground
        if self.element['in']:
            self.gnd += self.element['in', 'on']



from .. import Base
from bem import Transistor_Bipolar, Resistor, Capacitor, u, u_V
from skidl import Net
from math import pi


class Modificator(Base):
    """
    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 84
    """

    def mirror(self, programmer):
        mirror = Transistor_Bipolar(type='pnp', follow='collector', common='base')()
        stabilizer = Transistor_Bipolar(type='pnp', follow='collector', common='base')()
        mirroring = mirror.base & programmer.base & stabilizer

        V_je = (stabilizer.selected_part.spice_params.get('VJE', None) or 0.6) @ u_V
        self.R_g = (self.V_ref - V_je) / self.I_load
        generator = Resistor()(self.R_g, ref='R_g')
        sink = self.ref() & programmer & stabilizer.base & generator & self.gnd 
        v_ref = self.ref() & mirror 

        return stabilizer.output
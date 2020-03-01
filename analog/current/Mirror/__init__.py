
from bem.abstract import Electrical, Network
from bem.basic import Resistor
from bem.basic.transistor import Bipolar

from bem import u, u_ms, u_Ohm, u_A, u_V

from settings import params_tolerance
from random import randint

class Base(Electrical(), Network(port='two')):
    """**Bipolar Transistor Current Mirror**
    
    The technique of matched base–emitter biasing can be used to make what is called a current mirror, an interesting current-source circuit that simply reverses the sign of a “programming” current.

    You program the mirror by sinking a current from Q1’s collector. That causes a `V_(be)` for Q1 appropriate to that current at the circuit temperature and for that transistor type. Q2, matched to Q1,

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 86

    """

    pins = {
        'v_ref': ('Vref', ['input']),
        'output': True,
        'gnd': True
    }

    V_ref = 15 @ u_V
    V_drop = 0 @ u_V
    amount = 1
    Load = 0.001 @ u_A

    def willMount(self, V_ref, amount=1):
        """
        amount -- Number of different loads
        R_g -- An easy way to generate the control current `I_(load)` is with a resistor
        """
        self.load(self.V_ref)

    def circuit(self, **kwargs):
        programmer = Bipolar(type='pnp', follow='collector', common='base')()

        self.V_drop += (programmer.selected_part.spice_params.get('VJE', None) or 0.6) @ u_V

        mirror = self.mirror(programmer)
        load = mirror & self.output

    def ref(self):
        return self.input

    def mirror(self, programmer):
        self.R_g = (self.V_ref - self.V_drop) / self.I_load 
        mirror = Bipolar(type='pnp', follow='collector', common='base')()
        mirroring = mirror.base & programmer.base
        generator = Resistor()(self.R_g, ref='R_g')
        sink = self.ref() & programmer & programmer.base & generator & self.gnd 
        load = self.ref() & mirror 

        return mirror.output
from bem.abstract import Electrical
from bem.analog.voltage import Integrator, SchmittTrigger
from bem import u_Ohm

class Base(Electrical()):
    pins = {
        'input': True,
        'output': True,
        'v_ref': True,
        'v_inv': True,
        'gnd': True
    }
    def willMount(self, Load=10000@ u_Ohm):
        pass

    def circuit(self):
       ramp = Integrator(via='opamp')()
       driver = SchmittTrigger(via='opamp')(V_on=3, V_off=-3)

       driver & ramp & self.output & driver

       self.v_ref & driver.v_ref & ramp.v_ref
       self.gnd & driver.gnd & ramp.gnd
       self.v_inv & ramp.v_inv

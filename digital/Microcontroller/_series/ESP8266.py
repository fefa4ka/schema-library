from bem.abstract import Physical, Network
from .. import Base
from bem import u_uF, u_nF, u_kOhm, u_V, u_Hz
from bem.basic import Capacitor, Resistor

pins = {}
pins['ESP-07'] = {
    'RST': ['RESET'],
    'EN': ['CH_PD']
}

class Modificator(Network(interface=['uart']), Base):
    def willMount(self, V=3.3 @ u_V, frequency=80000000 @ u_Hz):
        pass

    def pins_alias(self):
        return pins[self.model]

    def circuit(self):
        self.element = self.part()
        self.v_ref & self['vcc']
        self.gnd & self.element['gnd']
        v_stable = self.v_ref & Capacitor()(100 @ u_uF) & self.gnd
        power_control = self.v_ref & Resistor()(10 @ u_kOhm) & self['EN']


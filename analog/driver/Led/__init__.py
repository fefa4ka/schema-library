from bem.abstract import Electrical, Network
# from bem.basic import Resistor
# from bem.basic.transistor import Bipolar
from inspect import _empty


class Base(Electrical()):
    props = { 'controlled': ['bipolar'] }
    diodes = []

    def willMount(self, diodes):
        if diodes == _empty:
            self.diodes = []
        elif type(diodes) != list:
            self.diodes = [diodes]

        """
        TODO: Controlled driver by led
        Load = 0 @ u_W
        for diode in self.diodes:
            Load += led.load(self.V - led.V_j)

        if 'bipolar' in self.props.get('controlled', []):
            self.input & Bipolar(type='npm')(base=Resistor(10 @ u_kOhm), Load=Load) & self.output
        """



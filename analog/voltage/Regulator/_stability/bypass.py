from bem.analog import Signal
from bem.basic import Capacitor
from bem import u_uF, u_F

models = {}

for model in ['ADJ', '1.2', '1.5', '1.8', '2.5', '3.3', '5.0']:
    models['AMS1117-' + model] = [10 @ u_uF, 22 @ u_uF]
    models['NCP1117-' + model] = [10 @ u_uF, 10 @ u_uF]

models['L7805'] = [0.33 @ u_uF, 0.1 @ u_F]

class Modificator:
    def circuit(self):
        if 'ic' not in self.mods.get('via', []):
            raise TypeError("Bypass capacitors using for IC. Regulator should build with via=ic modificator")

        super().circuit()

        def C_bypass(index):
            values = models[self.model]
            return Capacitor()(values[index])

        front = self.input & C_bypass(0) & self.gnd
        back = self.output & C_bypass(1) & self.gnd

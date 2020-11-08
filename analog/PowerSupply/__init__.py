from bem.abstract import Electrical, Network
from bem.analog.voltage import Rectifier, Regulator
from bem.basic import Transformer

from bem import u_V, u_Hz


class Base(Network(port=['two']), Electrical()):
    def willMount(self, V=220 @ u_V, V_out=5 @ u_V, Frequency = 60 @ u_Hz):
        self.V_stiff = self.V_out * 1.2
        pass

    def circuit(self):
        print(str(self.pins))
        transformer = Transformer()(V_out=self.V_stiff)
        # TODO: Fuses before
        # self.input & switch & fuse
        self.input & transformer.input
        self.input_n & transformer.input_n

        #transformer.output & load & transformer.output_n

        bridge = Rectifier(wave='full', rectifier='full')(
                V = self.V_stiff,
                V_ripple = 1 @ u_V,
                Frequency = self.Frequency
        )

        transformer & bridge

        # Filter
        # Regulator
        regulator = Regulator(via='ic', stability=['lowpass', 'bypass'])(
                V = self.V_stiff,
                V_out = self.V_out
        )
        bridge.output & regulator.input
        bridge.output_n & regulator.gnd

        self.output & regulator.output
        self.gnd & regulator.gnd & self.output_n

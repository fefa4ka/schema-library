from bem.basic import Resistor, Transistor_Bipolar
from bem import Net, u_Ohm
from bem.abstract import Electrical

class Base(Electrical()):
    """**Schmitt Trigger**
    TODO: Relaxation Oscillator https://en.wikipedia.org/wiki/Schmitt_trigger
    """

    R_in = 25000 @ u_Ohm
    R_out = 20 @ u_Ohm
    R_collector = 1000 @ u_Ohm

    def willMount(self, input=None):
        self.input = input or Net('SchmittTriggerInput')

    def circuit(self):
        self.gnd = Net()
        self.v_ref = Net()
        self.output = Net()

        regenerative = Transistor_Bipolar(type='npn', common='emitter')(
            base = Resistor()(self.R_in),
            collector = Resistor()(self.R_collector)
        )

        hysteresis = Transistor_Bipolar(type='npn', common='emitter')(
            collector = Resistor()(self.R_collector),
            emitter = Resistor()(self.R_out)
        )

        regenerative.gnd += hysteresis.emitter
        regenerative.output += hysteresis.input

        self.input += regenerative.input
        self.output += hysteresis.output

        self.gnd += hysteresis.gnd  
        self.v_ref += regenerative.v_ref, hysteresis.v_ref


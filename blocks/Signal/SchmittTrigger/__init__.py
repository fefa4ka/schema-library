from bem import Block, Resistor, Transistor_Bipolar, u_Ohm
from skidl import Net

class Base(Block):
    """**Schmitt Trigger**

    """

    R_in = 25000 @ u_Ohm
    R_out = 20 @ u_Ohm
    R_collector = 1000 @ u_Ohm

    def __init__(self, input=None):
        self.input = input or Net('SchmittTriggerInput')

        self.circuit()

    
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


    def test_sources(self):
        return super().test_sources() + [{
                'name': 'V',
                'args': {
                    'value': {
                        'value': 15,
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    }
                },
                'pins': {
                    'p': ['v_ref'],
                    'n': ['gnd']
                }
        }]
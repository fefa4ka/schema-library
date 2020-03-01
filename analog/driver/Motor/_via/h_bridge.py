from .. import Base
from bem.abstract import Network
from bem.basic import Diode
from bem.basic.transistor import Field
from bem import Net, u_V
from collections import defaultdict

class Modificator(Base, Network(port='two')):

    pins = {
        'input': 'ForwardSignal',
        'input_n': 'BackwardSignal',
        'output': 'LoadP',
        'output_n': 'LoadN',
        'v_ref': 'PowerSupply',
        'gnd': 'Ground'
    }

    def circuit(self):
        Transistor = Field(type='mosfet', channel='n')
        D = Diode(type='generic')

        for valign in ['top', 'bottom']:
            for halign in ['left', 'right']:
                input = self.input if (valign == 'top' and halign == 'left') or (valign == 'bottom' and halign == 'right') else self.input_n
                output = self.output if halign == 'left' else self.output_n

                section = input & Transistor(
                    drain = output if valign == 'bottom' else self.v_ref,
                    source = output if valign == 'top' else self.gnd
                )

        for pin in [self.output, self.output_n]:
            protect = pin & D(**self.load_args)['A, K'] & self.v_ref
            protect_gnd = self.gnd & D(**self.load_args)['A, K'] & pin


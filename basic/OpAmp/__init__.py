from bem import Build, Net
from bem.abstract import Physical, Network
from skidl import Part, TEMPLATE
from skidl.Net import Net as NetType
from PySpice.Unit import u_Ohm, u_uF, u_H, u_Hz

class Base(Physical(), Network(port='two')):
    """
        Operational amplifiers are linear devices that have all the properties
        required for nearly ideal DC amplification and are therefore used extensively
        in signal conditioning, filtering or to perform mathematical operations
        such as add, subtract, integration and differentiation.
    """


    """
        An Operational Amplifier is basically a three-terminal device which consists
        of two high impedance inputs. One of the inputs is called the Inverting Input,
        marked with a negative or “minus” sign, ( – ).
        The other input is called the Non-inverting Input, marked with a positive or “plus” sign ( + ).
    """
    pins = {
        'input': True,
        'input_n': True,
        'v_ref': True,
        'output': True,
        'gnd': True
    }

    frequency = 100 @ u_Hz

    def willMount(self, frequency=None):
        pass

    def circuit(self):
        self.element = self.part()

        # part['input'] += self.input
        # part['input_n'] += self.input_n
        # part['output'] += self.output
        # part['v_ref'] += self.v_ref
        # part['gnd'] += self.gnd

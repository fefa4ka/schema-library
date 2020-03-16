from bem.abstract import Physical, Network
from PySpice.Unit import u_Hz
from math import pi


class Base(Physical(), Network(port='two')):
    """
        # Operational Amplifier
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
        'v_inv': True,
        'output': True,
        'gnd': True
    }

    def willMount(self, Frequency=1e3 @ u_Hz):
        """
            V -- Verify that the amplifier can achieve the desired output swing using the supply voltages provided
            slew_rate -- The rate of change in the output voltage caused by a step change on the input.
        """
        self.slew_rate = 2 * pi * self.Frequency * self.V

    def circuit(self):
        self.element = self.part()

        # buffer.v_ref & self.v_ref
        # if 'single' in self.props.get('supply', []):
        #     split_power = Divider(type='resistive')(
        #         V=self.V,
        #         V_out=self.V / 2,
        #         Load=source.value)
        #     self.v_ref & split_power & buffer
        #     buffer.gnd & self.gnd & split_power.gnd
        # else:
        #     buffer.input & self.gnd
        #     buffer.gnd & self.v_inv
       

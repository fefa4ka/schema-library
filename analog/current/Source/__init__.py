
from bem.abstract import Electrical, Virtual
from bem.analog.voltage import Divider, Regulator
from bem.basic import Resistor, Diode, OpAmp
from bem.basic.transistor import Bipolar
from bem import u, u_ms, u_Ohm, u_A, u_V
from bem.utils.args import has_prop

from settings import params_tolerance
from random import randint


class Base(Electrical(port='two')):
    """# Transistor Current Source
    Happily, it is possible to make a very good current source with a transistor. It works like this: applying `V_b` to the base, with `V_b>0.6 V`, ensures that the emitter is always conducting:
    
    The base voltage can be provided in a number of ways: a voltage divider is ok, as long as it is stiff enough, or you can use a zener diode.
    
    A current source can provide constant current to the load only over some finite range of load voltage. To do otherwise would be equivalent to providing infinite power.

    `V_e = V_b − 0.6 V`
    so
    `I_e = V_e / R_e = (V_b − 0.6 V) / R_e`

    But, since `I_e ≈ I_(load)` for large beta,
    `I_(load) ≈ (V_b − 0.6 V) / R_e`
    
    ```
    from bem.basic import Diode

    v_ref = VS(flow='V')(10)

    load = Diode(type='generic')()
    source = Example()
    
    v_ref & source & load & source.output_n

    
    watch = source
    ```

    * Paul Horowitz and Winfield Hill. "2.2.5 Emitter follower biasing" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, p. 86

    """ 

    props = {
        'via': ['bipolar', 'opamp'],
        'stiff': ['resistive', 'zener'] 
    }

    pins = {
        'v_ref': ('Vref', ['input']),
        'input_n': True,
        'output': True,
        'output_n': True,
        'gnd': True
    }


    def willMount(self, Load=0.001 @ u_A):
        """

        """
        self.load(self.V)

    def circuit(self, **kwargs):
        is_stiff = lambda mode: has_prop(self, 'stiff', mode)
        via = self.props.get('via', ['bipolar'])

        if 'opamp' in via:
            generator = OpAmp()()
            generator.v_ref & self.input
            generator.v_inv & self.input_n
            generator.V_je = 0
            generator.Beta = 1000

        elif 'bipolar' in via:
            generator = Bipolar(type='npn', follow='emitter')()
            generator.collector += self.output_n

        if is_stiff('zener'):
            controller = Regulator(via='zener', upper_limit="BV")(
                V_out=self.V / 2,
                Load=self.I_load / generator.Beta
            )
            self.V_b = controller.V_out
            self.V_e = self.V_b - generator.V_je

        elif is_stiff('diode_drop'):
            """
            TODO: With pnp transistor
            drop = Diode(type='generic')
            drop_input = drop()
            drop_middle = drop()
            drop_output = drop()
            drop_input & drop_middle & drop_output
            controller = Virtual()(
                input=drop_input.input,
                output=drop_output.output,
                gnd=self.gnd
            )
            # TODO: Add resistor current drivers for diodes
            self.V_b = self.V - (drop_input.V_j + drop_middle.V_j + drop_output.V_j)
            self.V_e = self.V_b - generator.V_je
            """

        else:
            self.V_e = generator.V_je + randint(1, int(u(self.V) / 2)) @ u_V
            self.V_b = self.V_e + generator.V_je

            #  The criterion is that its impedance should be much less than the dc impedance looking into the base (`β RE`).
            controller = Divider(type='resistive')(
                V_out = self.V_b,
                Load = self.I_load / (generator.Beta / 10)
            )


        if 'opamp' in via and 'bipolar' in via:
            if is_stiff('zener'):
                pass
            else:
                self.R_e = self.V * controller.R_in / (self.I_load * (controller.R_in + controller.R_out))
        else:
            self.R_e = self.V_e / self.I_load

        source = Resistor()(self.R_e)
        controller.output & generator
        if 'opamp' in via:
            if 'bipolar' in via:
                amplifier = Bipolar(type='pnp', follow='collector')()
                generator.output & amplifier & self.output
                amplifier.emitter & generator.input_n & source & self.v_ref
                self.output_n & self.gnd
            elif 'mosfet' in via:
                amplifier = None
            else:
                generator & self.output
                generator.input_n & self.output_n & source & self.gnd

        elif 'bipolar' in via:
            generator & source & self.gnd

        controller.input += self.v_ref
        controller.gnd += self.gnd

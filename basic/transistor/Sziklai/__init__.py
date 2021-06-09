from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical
from bem.basic.transistor import Bipolar
from bem.basic import Resistor

class Base(Electrical()):
    """# Sziklai Transistor Connection

    By attaching two transistors together, a larger current-handling, larger `h_(FE)` equivalent transistor circuit is formed.
    The combination is referred to as a Darlington pair. The equivalent `h_(FE)` for the pair is equal to the product of the individual transistor’s `h_(FE)` values (`h_(FE) = h_(FE1)h_(FE2)`. 
    
    Darlington pairs are used for large current applications and as input stages for amplifiers, where big input impedances are required.
    Unlike single transistors, however, Darlington pairs have slower response times (it takes longer for the top transistor to turn the lower transistor on and off) and have twice the base-to-emitter voltage drop (1.2 V instead of 0.6 V) as compared with single transistors. 

    Darlington pairs can be purchased in single packages.

    ```
    vs = VS(flow='V')(V=10)

    load = Resistor()(1000)
    darlington = Example()

    vs & darlington & load & vs.gnd

    watch = regulator
    ```
    """

    def circuit(self):
        driver = Bipolar(type='npn', follow='collector')()
        amplifier = Bipolar(type='pnp', follow='collector')()

        self.input & driver & amplifier & self.output

        driver['emitter'] & self.output
        amplifier['emitter'] & self.v_ref

        self.v_ref & Resistor()(100) & amplifier




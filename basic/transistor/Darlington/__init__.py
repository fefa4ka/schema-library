from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical, Virtual
from bem.basic.transistor import Bipolar

class Base:
    """# Darlington Transistor Connection

    By attaching two transistors together, a larger current-handling, larger `h_(FE)` equivalent transistor circuit is formed.
    The combination is referred to as a Darlington pair. The equivalent `h_(FE)` for the pair is equal to the product of the individual transistor’s `h_(FE)` values (`h_(FE) = h_(FE1)h_(FE2)`. 
    
    Darlington pairs are used for large current applications and as input stages for amplifiers, where big input impedances are required.
    Unlike single transistors, however, Darlington pairs have slower response times (it takes longer for the top transistor to turn the lower transistor on and off) and have twice the base-to-emitter voltage drop (1.2 V instead of 0.6 V) as compared with single transistors. 

    Darlington pairs can be purchased in single packages.

    ```
    # Fixme
    vs = VS(flow='V')(V=10)

    load = Resistor()(1000)
    darlington = Example()

    vs & darlington & load & vs.gnd

    watch = darlington
    ```
    """

    props = {
        'type': ['npn', 'pnp'],
        'emitter': ['follower', 'amplifier']
    }

    inherited = [Bipolar]
    selected_part = True
    _available_parts = []

    def circuit(self):
        self.emitter = None
        self.base = None
        self.collector = None

        bjt_type = self.props.get('type', 'npn')
        if bjt_type == 'npn':
            bjt = Bipolar(type='npn', common='emitter', follow='emitter')
            driver = bjt()
            amplifier = bjt()
            driver.output & amplifier
            driver.v_ref & amplifier.v_ref

            transistor = Virtual()(collector=amplifier.v_ref,
                                   emitter=amplifier.output,
                                   base=driver.input)
        else:
            driver = Bipolar(type=bjt_type, common='collector', follow='emitter')()
            amplifier = Bipolar(type=bjt_type, common='collector', follow='collector')()
            driver & amplifier

            transistor = Virtual()(collector=amplifier['collector'],
                                   emitter=amplifier['emitter'],
                                   base=driver.input)


        transistor.BF = driver.Beta * amplifier.Beta
        transistor.VJE = driver.V_je
        transistor.VCE = driver.V_ce

        self._part = transistor

        super().circuit()

from bem.abstract import Electrical, Network


class Base(Electrical(), Network(port='two')):
    """
    # Differential amplifier

    The differential amplifier shown here is a device that compares two separate input signals, takes the difference between them, and then amplifies this difference. In the ideal case the output is entirely independent of the individual signal levels – only the difference matters. The differential amplifier is sometimes called a “long-tailed pair.”

    To understand how the circuit works, treat both transistors as identical, and then notice that both transistors are set in the common-emitter configuration. 

    Differential amplifiers are important in applications in which weak signals are contaminated by “pickup” and other miscellaneous noise.

    When both inputs change levels together, that’s a _common-mode_ input change. A differential change is called _normal mode_, or sometimes _differential mode_.

    ```
    # Power supply
    v_ref = VS(flow='V')(V=10)
    v_inv = VS(flow='V')(V=-10)

    # Signals
    signal_1 = VS(flow='SINEV')(V=0.2, frequency=120)
    signal_2 = VS(flow='SINEV')(V=0.3, frequency=1200)

    # Load
    load = Resistor()(1000)

    # Amplifier
    diff = Example() 

    # Network
    v_ref & diff.v_ref
    v_inv & diff.v_inv

    signal_1 & diff.input
    signal_2 & diff.input_n

    diff.output & load & v_ref

    diff.gnd & v_inv.gnd & v_ref.gnd & signal_1.gnd & signal_2.gnd

    watch = diff
    ```

    * Paul Horowitz and Winfield Hill. "2.3.8 Differential amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 102-104
    """

    mods = {
        'via': ['bipolar']
    }


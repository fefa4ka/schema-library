from bem import u_V
from bem.abstract import Electrical


class Base(Electrical()):
    """# Voltage Regulator

    ```
    vs = VS(flow='V')(V=10)

    load = Resistor()(1000)
    regulator = Example()

    vs & regulator & load & vs.gnd

    watch = regulator
    ```
    """
    def willMount(self, V_out=3.3 @ u_V):
        self.load(V_out)


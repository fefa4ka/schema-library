

from bem import Net, u, u_W, u_Ohm, u_V
from bem.abstract import Electrical
from bem.basic import Diode, Resistor

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


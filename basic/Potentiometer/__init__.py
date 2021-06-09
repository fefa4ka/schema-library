from PySpice.Unit import u_Ohm, u_V
from bem import Build
from bem.abstract import Combination


class Base(Combination(port='two')):
    """
    # Potentiometer 


    ```
    vs = VS(flow='SINEV')(V=5, frequency=120)
    resistor = Example()
    load = Resistor()(1000)

    vs & resistor & load & vs

    watch = load
    ```

    """
    increase = True

    def willMount(self, value=10000 @ u_Ohm, V=12 @ u_V):
        """
            value -- A maximum resistance of potentiometer
            V_drop -- Voltage drop after resistor with Load
        """
        self.Power = self.value
        self.consumption(self.V)

        # Power Dissipation
        I_total = self.V / (self.R_load + self.value)
        self.V_drop = self.value * I_total

        self.load(self.V - self.V_drop)

    def part_spice(self, *args, **kwargs):
        return Build('R').spice(*args, **kwargs)

    def circuit(self):
        super().circuit()

        self.input & self.element[1]
        self.output & self.element[2]
        self.input_n & self.output_n & self.element[3]


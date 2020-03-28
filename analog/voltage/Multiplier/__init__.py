from bem.abstract import Electrical 
from bem.analog.voltage import Rectifier
from bem import Net
from PySpice.Unit import u_ms, u_V, u_A, u_Hz, u_Ohm

class Base(Electrical()):
    """# Voltage Double, Tripler, Quadrupler, etc

    Voltage doubler. Think of it as *two half-wave rectifier circuits* in series.

    Variations of this circuit by argument Scale exist for voltage triplers, quadruplers, etc. )

    ```
        vs = VS(flow='SINEV')(V=5, frequency=120)
        load = Resistor()(1000)

        doubler = Example()
        # triplers = Multiplier()(Scale=3, Frequency=120)
        # quadruplers = Multiplier()(Scale=4, Frequency=120)

        vs & doubler & load & vs

        watch = doubler
    ```

    You can extend this scheme as far as you want, producing what’s called a Cockcroft–Walton generator; these are used in arcane applications (such as particle accelerators) and in everyday applications (such as image intensifiers, air ionizers, laser copiers, and even bug zappers) that require a high dc voltage but hardly any current.

        * Paul Horowitz and Winfield Hill. "1.6.4 Rectifier configurations for power supplies" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 33-35
    """

    def willMount(self, Scale=2, Frequency=120 @ u_Hz, V_ripple=1 @ u_V):
        self.input_n = self.gnd

        self.load(self.V * self.Scale)

    def circuit(self):
        HalfBridge = Rectifier(wave='half', rectifier='full')

        sections = []

        if self.Scale % 2:
            sections.append((self.input_n, self.input))
        else:
            sections.append((self.input, self.input_n))

        for block in range(int(self.Scale)):
            last = sections[-1]

            scaler = HalfBridge(
                V=self.V * self.Scale,
                frequency=self.Frequency,
                V_ripple=self.V_ripple
            )
            scaler.gnd += last[0]
            scaler.input += last[1]

            sections.append((scaler.input, scaler.output))

        self.output += sections[-1][1]

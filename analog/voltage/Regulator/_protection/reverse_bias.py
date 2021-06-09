
from .. import Base
from bem.basic import Diode


class Modificator(Base):
    """## Reverse-Bias-Protection Circuit

    Occasionally, the input voltage to the regulator can collapse faster than the output voltage. This can occur, for
    example, when the input supply is crowbarred during an output overvoltage condition. If the output voltage is
    greater than approximately 7 V, the emitter-base junction of the series-pass element (internal or external) could
    break down and be damaged. To prevent this, a diode shunt can be used

    * LM7805 datasheet / https://www.sparkfun.com/datasheets/Components/LM7805.pdf

    """
    def circuit(self):
        super().circuit()

        protector = self.output & Diode(type='generic')() & self.input

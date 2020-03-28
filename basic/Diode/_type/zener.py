from .. import Base
from bem import u_A

class Modificator(Base):
    """
    * https://github.com/peteut/spice-models/blob/master/diodes/diodes/diodes_zener-diodes.txt
    * http://espice.ugr.es/espice/src/modelos_subckt/spice_complete/cadlab.lib
    * https://www.electronics-notes.com/articles/electronic_components/diode/zener-diode-datasheet-specifications-parameters.php

    """
    def circuit(self):
        self.I_max = float(self['P']) / float(self['BV']) @ u_A
        
        super().circuit()

from bem import Build
from bem.abstract import Electrical
from lcapy import log10

class Base(Electrical()):
    mods = {
        'flow': 'dc'
    }

    def __mod__(self, other):
        """Decibels
        
        Arguments:
            other {Signal} -- the signal compared with
        
        Returns:
            [float] -- Compared the relative amplitudes in dB of two Signals
        """
        return 20 * log10(other.amplitude / self.amplitude)


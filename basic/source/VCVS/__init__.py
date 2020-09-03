from bem.abstract import Electrical
from lcapy import log10
from copy import copy

class Base(Electrical()):
    device = ''

    def willMount(self, gain=''):
        """
        gain -- `V_(out) = V * gain`
        """
        pass

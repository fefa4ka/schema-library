from bem import Build
from bem.abstract import Physical 
from skidl import Part, TEMPLATE
from PySpice.Unit import u_Hz

class Base(Physical()):
    """
    """
    frequency = 8000000 @ u_Hz

    def willMount(self, frequency):
        pass

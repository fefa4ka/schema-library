from bem import Build, u_Ohm, u_A, u_V
from skidl import Part, TEMPLATE
from bem.abstract import Physical


class Modificator(Physical()):
    """## Physical Switch Input
    
    Switch connected series to the signal.
    """

    def part_spice(self, *args, **kwargs):
        return Build('VCS').spice(*args, **kwargs)


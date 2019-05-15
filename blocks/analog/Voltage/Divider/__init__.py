from bem import u_Ohm, u_V, u_A
from bem.abstract import Electrical

class Base(Electrical()):
    """**Voltage Divider**

    Voltage divider from `V_(\i\\n)` to `V_(out)` could be implemented in different ways and provide current `I_(out)`.
    """

    # Props
    V_out = 3 @ u_V

    mods = {
        'type': ['resistive']
    }

    def willMount(self, V_out):
        """
           V_out -- Note that the output voltage is always less than (or equal to) the input voltage; that’s why it’s called a divider.
        """
        self.load(self.V_out)
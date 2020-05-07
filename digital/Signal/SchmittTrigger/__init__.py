from bem import Net, u_Ohm, u_A, u_V
from bem.abstract import Electrical


class Base(Electrical()):
    """
    A Schmitt trigger is a decision-making circuit. It is used to convert a slowly varying analogue signal voltage into one of two possible binary states, depending on whether the analogue voltage is above or below a preset threshold value. A comparator can do much the same job.

    * https://en.wikipedia.org/wiki/Schmitt_trigger
    """

    def willMount(self, Load=10000 @ u_Ohm, V_on=7 @ u_V, V_off=3 @ u_V):
        pass


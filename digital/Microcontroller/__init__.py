from bem import Block, Build, u_B, u_Hz
from bem.abstract import Physical, Network
from skidl import Part, Net, TEMPLATE

class Base(Physical()):
    """

    ```
    vs = VS(flow='V')(V=5)
    mcu = Microcontroller(series='ATmega8')()
    vs & mcu.v_ref
    mcu.gnd & vs

    watch = mcu 
    ```
    """
    mods = {
        'series': 'ATmega8'
    }

    def willMount(self, frequency=12000000 @ u_Hz):
        pass



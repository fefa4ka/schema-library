from bem import Block, Build, u_B, u_Hz, u_V
from bem.abstract import Physical, Network
from skidl import Part, Net, TEMPLATE

class Base:
    inherited = Physical

    """

    ```
    vs = VS(flow='V')(V=5)
    mcu = Example()
    vs & mcu.v_ref
    mcu.gnd & vs

    watch = mcu
    ```
    """

    def mount(self, *args, **kwargs):
        super().mount(*args, **kwargs)

        self.set_pins_aliases(self.pins_alias())

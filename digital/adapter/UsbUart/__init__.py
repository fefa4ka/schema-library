from bem import Block
from bem.abstract import Electrical, Network
from bem.basic import Plug


class Base(Network(interface=['uart', 'usb']), Electrical()):
    """

    ```
    vs = VS(flow='V')(V=5)
    adapter = Example()
    vs & adapter.v_ref
    adapter.gnd & vs

    watch = adapter
    ```
    """
    pins = {
        'v_ref': True,
        'gnd': True,
        'D+': True,
        'D-': True,
        'RX': True,
        'TX': True
    }


from bem import Block
from bem.abstract import Electrical, Network
from bem.basic import Plug


class Base(Network(interface=['uart', 'usb']), Electrical()):
    pins = {
        'v_ref': True,
        'gnd': True,
        'D+': True,
        'D-': True,
        'RX': True,
        'TX': True
    }


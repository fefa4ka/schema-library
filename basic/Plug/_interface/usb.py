from .. import Base
from bem.abstract import Network

class Modificator(Base, Network(interface='usb')):
    props = {
        'type': ['a', 'b'],
	'size': ['default', 'mini', 'micro']
    }


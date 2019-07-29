from .. import Base
from bem.abstract import Network

class Modificator(Base, Network(interface='usb')):
    type = 'a'
    size = 'default'

    def willMount(self, type='b', size=None):
        pass


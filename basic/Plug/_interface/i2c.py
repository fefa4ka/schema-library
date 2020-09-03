from .. import Base
from bem.abstract import Network

class Modificator(Base, Network(interface='i2c')):
    pass


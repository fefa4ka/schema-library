from bem.abstract import Network
from .. import Base

class Modificator(Base, Network(interface='uart')):
    pass


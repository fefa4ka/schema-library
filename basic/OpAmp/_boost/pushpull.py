from .. import Base
from bem.analog.voltage import PushPull
from skidl import Net


class Modificator(Base):
    def circuit(self):
        super().circuit()

        output = Net('BoostedOpAmp')
        boost = self & PushPull(stability='crossover')() & output
        self.output = output

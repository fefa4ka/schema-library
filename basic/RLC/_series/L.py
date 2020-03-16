from .. import Base
from bem.basic import Inductor
from bem import Net
from PySpice.Unit import u_H

class Modificator(Base):
    def willMount(self, L_series=1 @ u_H):
        pass

    def circuit(self):
        super().circuit()

        signal = self.output
        self.output = Net('SeriesInductorOutput')

        L_series = signal & Inductor()(self.L_series) & self.output

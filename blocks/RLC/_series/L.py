from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_H

class Modificator(Base):
    L_series = 1 @ u_H

    def __init__(self, L_series, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.L_series = L_series

    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SeriesInductorOutput')

        L = Build('Inductor').block
        
        L_out = L(value=self.L_series, ref='L_s')

        circuit = signal & L_out['+,-'] & self.output 
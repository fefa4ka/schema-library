from .. import Base, Build
from skidl import Net
from PySpice.Unit import u_F

class Modificator(Base):
    C_series = 1 @ u_F

    def __init__(self, C_series, *args, **kwargs):
        self.C_series = C_series

        super().__init__(*args, **kwargs)
        
    def circuit(self):
        super().circuit()
        
        signal = self.output
        self.output = Net('SeriesCapacitorOutput')

        C = Build('Capacitor').block
        
        C_out = C(value=self.C_series, ref='C_s')

        circuit = signal & C_out['+', '-'] & self.output 
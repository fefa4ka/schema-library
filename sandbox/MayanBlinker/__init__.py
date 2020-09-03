from skidl import Net
from bem import u_V, u_A
from bem.abstract import Electrical
from bem.basic.oscillator import Multivibrator
from bem.basic import Diode, Resistor

class Base(Electrical()):
    """
    **Mayan Calendar Symbol Eye Blinker**
    
    Blinking eyes with duty cycle related to birthday. set_width = month / 10 part reset_width = day / 10
    """
    V = 3.4 @ u_V
    Load = 0.02 @ u_A

    month = 6
    day = 21


    def willMount(self, month, day):
        pass

    def circuit(self):
        def Eye(signal, color):
            led = Diode(type='led')(V=self.V, Load=self.Load, color=color)
            controller = Resistor()(self.V / self.Load)

            signal & led & controller & self.gnd
            
        blinker = Multivibrator(state='astable')(
            V=self.V,
            Load=self.Load,
            V_load=2.2 @ u_V,
            set_period=self.month / 10,
            reset_period=self.day / 10
        )

        # self & blinker
        self.v_ref = blinker.v_ref
        self.gnd = blinker.gnd
        # 
        # Eye(blinker.output, 'red')
        # Eye(blinker.output_n, 'green')
        self.output_n = Net('OutN')
        self.output = blinker.output
        self.output_n = blinker.output_n


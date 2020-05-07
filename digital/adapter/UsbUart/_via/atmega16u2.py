from .. import Base
from bem.abstract import Network
from bem.digital import Microcontroller
from bem.basic import Plug, Diode
from bem.analog.driver import Led
from bem import u_MHz

class Modificator(Base):
     def circuit(self):
        mcu = self & Microcontroller(series='ATmega8U2')(model='ATmega16U2', frequency=16 @ u_MHz)
        mcu['D+'] & self['D+']
        mcu['D-'] & self['D-']
        self.element = mcu

        spi = mcu & Plug(interface='spi')()

        tx_led = self.v_ref & Led(via='resistor')(diodes=Diode(type='led')(color='green')) & mcu['PD5']
        rx_led = self.v_ref & Led(via='resistor')(diodes=Diode(type='led')(color='red')) & mcu['PD4']


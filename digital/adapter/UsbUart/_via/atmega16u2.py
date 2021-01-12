from bem.digital import Microcontroller
from bem.basic import Plug, Diode
from bem.analog.driver import Led
from bem import u_MHz, u_V, u_MOhm


class Modificator:
     def circuit(self):
        mcu = self & Microcontroller(series='ATmega8U2')(model='ATmega16U2', V=5 @ u_V, frequency=16 @ u_MHz)
        mcu['D+'] & self['D+']
        mcu['D-'] & self['D-']
        self.element = mcu

        spi = mcu & Plug(interface='spi')()

        def led(color):
            diode = Diode(type='led')(color=color)
            driver = Led(via='resistor')(diodes=diode)

            return driver

        tx_led = self.v_ref & led('green') & mcu['TX']
        rx_led = self.v_ref & led('red') & mcu['RX']


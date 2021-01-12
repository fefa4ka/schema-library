from bem.basic import Resistor
from bem import u_Ohm
from skidl import Net

class Modificator:
    mods = { 'interface': 'spi' }

    def spi(self, instance):
        """
        If additional devices are connected to the ISP lines, the programmer must be protected from any device
        that may try to drive the lines, other than the AVR. This is important with the SPI bus, as it is similar to the
        ISP interface. Applying series resistors on the SPI lines, as depicted in Connecting the SPI Lines to the
        ISP Interface, is the easiest way to achieve this. Typically, the resistor value R can be of 330Ω
        """

        mosi = Net('MOSI')
        miso = Net('MISO')
        sck = Net('SCK')

        isp_mosi = self['MOSI'] & Resistor()(330 @ u_Ohm) & mosi & instance['MOSI']
        isp_miso = self['MISO'] & Resistor()(330 @ u_Ohm) & miso & instance['MISO']
        isp_sck = self['SCK'] & Resistor()(330 @ u_Ohm) & sck & instance['SCK']

        for pin in ['MOSI', 'MISO', 'SCK']:
            instance[pin].disconnect()
            instance_pin = instance[pin]
            instance_pin += self[pin]

        self.MOSI = mosi
        self.MISO = miso
        self.SCK = sck

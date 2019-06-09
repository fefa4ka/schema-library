from ..interface import Interfaced
from bem.basic import Resistor
from bem import u_Ohm
from skidl import Part, Net

class Modificator(Interfaced):
    """
        * Atmel. "4.1 SPI Programming Interface" AVR042: AVR Hardware Design Considerations, 2016, p. 8"
    """

    SPI = ['SCK', 'MISO', 'MOSI', 'SS']

    def spi(self, instance):
        self.interface('SPI', instance)

    def spi_connector(self):
        connector = Part('Connector_Generic', 'Conn_02x05_Odd_Even', footprint='Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical', ref='SPI')

        """
        If additional devices are connected to the ISP lines, the programmer must be protected from any device
        that may try to drive the lines, other than the AVR. This is important with the SPI bus, as it is similar to the
        ISP interface. Applying series resistors on the SPI lines, as depicted in Connecting the SPI Lines to the
        ISP Interface, is the easiest way to achieve this. Typically, the resistor value R can be of 330Ω
        """
        def bus_protect():
            return Resistor()(330 @ u_Ohm)

        mosi = Net('MOSI')
        miso = Net('MISO')
        sck = Net('SCK')

        isp_mosi = self['MOSI'] & connector[1] & bus_protect() & mosi
        isp_miso = self['MISO'] & connector[9] & bus_protect() & miso
        isp_sck = self['SCK'] & connector[7] & bus_protect() & sck

        connector[2] += self.v_ref
        connector[5] += self['RESET']
        connector[6] += self.gnd

        self.MOSI = mosi
        self.MISO = miso
        self.SCK = sck
        
        return connector
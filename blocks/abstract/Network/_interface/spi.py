from ..interface import Interfaced
from bem.basic import Resistor
from bem import u_Ohm
from skidl import Part, Net
import sys, time, pylibftdi as ftdi

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

        mosi = Net('MOSI')
        miso = Net('MISO')
        sck = Net('SCK')

        isp_mosi = self['MOSI'] & connector[1] & Resistor()(330 @ u_Ohm) & mosi
        isp_miso = self['MISO'] & connector[9] & Resistor()(330 @ u_Ohm) & miso
        isp_sck = self['SCK'] & connector[7] & Resistor()(330 @ u_Ohm) & sck

        connector[2] += self.v_ref
        connector[5] += self['RESET']
        connector[6] += self.gnd

        self.MOSI = mosi
        self.MISO = miso
        self.SCK = sck

        return connector


    # def set_device(self):

    # # Set mode (bitbang / MPSSE)
    # def set_bitmode(d, bits, mode):
    #     return (d.setBitMode(bits, mode) if FTD2XX else
    #                 d.ftdi_fn.ftdi_set_bitmode(bits, mode))
 
    # # Open device for read/write
    # def ft_open(index=0):
    #     d = ftdi.Device(device_index=index)
    #     return d
 
    # # Set SPI clock rate
    # def set_spi_clock(d, hz):
    #     div = int((12000000 / (hz * 2)) - 1)  # Set SPI clock
    #     ft_write(d, (0x86, div%256, div//256)) 
    
    # # Read byte data into list of integers
    # def ft_read(d, nbytes):
    #     s = d.read(nbytes)
    #     return [ord(c) for c in s] if type(s) is str else list(s)
    
    # # Write list of integers as byte data
    # def ft_write(d, data):
    #     s = bytes(data)
    #     return d.write(s)
    
    # # Write MPSSE command with word-value argument
    # def ft_write_cmd_bytes(d, cmd, data):
    #     n = len(data) - 1
    #     ft_write(d, [cmd, n%256, n//256] + list(data))

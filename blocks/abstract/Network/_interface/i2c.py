from ..interface import Interfaced
from bem import u_kOhm
from bem.basic import Resistor
from skidl import Part

class Modificator(Interfaced):
    I2C = ['SCL', 'SDA']

    def i2c(self, instance):
        def pull_up():
            support = Net('PullUpSupport')
            pull_up = self.v_ref & Resistor()(4.7 @ u_kOhm) & support

            return support

        scl = self['SCL'] & pull_up() & instance['SCL']
        sda = self['SDA'] & pull_up() & instance['SDA']
          
    def i2c_connector(self):
        connector = Part('Connector_Generic', 'Conn_01x02', footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', ref='I2C')

        connector[1] += self['SCL']
        connector[2] += self['SDA']

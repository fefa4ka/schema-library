from .. import Base
from bem import Resistor, Capacitor, RLC
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Base):
    """**Pusle on signal hight**

    Pulse width depends by C and limited by input signal pulse duration.
    """

    C_width = 0.000001 @ u_F
    R_sensor_in = 10000 @ u_Ohm
    R_sensor_collector = 1000 @ u_Ohm
    R_pulse_base = 10000 @ u_Ohm
    R_pulse_collector = 1000 @ u_Ohm

    def circuit(self):
        super().circuit()
        
        sensor = Bipolar(type='npn', common='emitter')(
            base = Resistor()(self.R_sensor_in),
            collector = Resistor()(self.R_sensor_collector),
        )
        
        self.C_width = (self.width.value * self.width.scale / self.R_pulse_base.value * self.R_pulse_base.scale) * 1.4
        pulsar_width = RLC(series='C', vref='R')(
            C_series = self.C_width,
            R_vref = self.R_pulse_base)
        
        sensor.v_ref += self.v_ref, pulsar_width.v_ref
        sensor.gnd += self.gnd

        pulsar = Bipolar(type='npn', common='emitter')(
            base = pulsar_width,
            collector = Resistor()(self.R_pulse_collector)
        )
        
        pulse = self & sensor & pulsar

        self.output = Net('onHightPulse')
        pulsar.output += self.output
    
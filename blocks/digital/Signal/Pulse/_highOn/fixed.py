from .. import Base, Net
from bem.basic import Resistor, Capacitor, RLC
from bem.basic.transistor import Bipolar
from PySpice.Unit import u_Ohm, u_V, u_A, u_F

class Modificator(Base):
    """**Pusle with fixed width on signal hight**

    Pulse width determined by C
    """

    C_width = 0.000001 @ u_F
    R_sensor_in = 10000 @ u_Ohm
    R_sensor_collector = 1000 @ u_Ohm
    R_pulse_base = 10000 @ u_Ohm
    R_pulse_collector = 1000 @ u_Ohm
    R_holder_base = 20000 @ u_Ohm

    def circuit(self):
        super().circuit()
        
        sensor = Bipolar(type='npn', common='emitter')(
            base = Resistor()(self.R_sensor_in),
            collector = Resistor()(self.R_sensor_collector),
        )

        holder = Bipolar(type='npn', common='emitter')(
            base = Resistor()( self.R_holder_base)
        )

        self.C_width = (self.width / self.R_pulse_base) * 1.4
        pulsar_width = RLC(series='C', vref='R')(
            C_series = self.C_width,
            R_vref = self.R_pulse_base)

        pulsar = Bipolar(type='npn', common='emitter')(
            base = pulsar_width,
            collector = Resistor()(self.R_pulse_collector)
        )
    
        sensor.v_ref += self.v_ref, pulsar_width.v_ref
        sensor.gnd += self.gnd, holder.gnd

        holder.v_ref += sensor.output
        pulse = self & sensor & pulsar

        self.output = Net('onHightPulse')
        pulsar.output += self.output, holder.input
    
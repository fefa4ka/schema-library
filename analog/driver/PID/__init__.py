from bem.abstract import Electrical
from bem.analog.voltage import Summer, Inverter, Integrator, Differentiator, Difference
from bem import u_Hz

class Base(Electrical()):
    """
        * https://www.nutsvolts.com/magazine/article/the_pid_controller_part_1
        * http://www.ecircuitcenter.com/Circuits/op_pid/op_pid.htm
        * http://www.ecircuitcenter.com/Circuits/pid1/pid1.htm
        * file:///Users/fefa4ka/Yandex.Disk.localized/%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8/op_amp_pid_paper_MATEC_FORMAT.pdf
    """
    pins = {
        'v_ref': True,
        'set': ('SetPoint', ['input']),
        'sensor': True,
        'output': True,
        'v_inv': True,
        'gnd': True
    }

    def willMount(self, Gain=2, Frequency=100 @ u_Hz):
        pass

    def circuit(self):
        params = {
            'Gain': self.Gain,
            'Frequency': self.Frequency
        }

        loss = Difference(via='opamp')(**params)

        proportional = Inverter(via='opamp')(**params)
        integral = Integrator(via='opamp')(**params)
        derivative = Differentiator(via='opamp')(**params)

        self.set & loss.input
        self.sensor & loss.input_n

        loss.output & proportional.input & integral.input
        self.sensor & derivative

        pid = Summer(via='opamp')(inputs=[proportional, integral, derivative], **params)
        pid & self.output

        # Power supply
        parts = [loss, proportional, integral, derivative, pid]
        for part in parts:
            self.v_ref & part.v_ref
            self.v_inv & part.v_inv
            self.gnd & part.gnd

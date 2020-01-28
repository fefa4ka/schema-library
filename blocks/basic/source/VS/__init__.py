from bem import Build
from bem.abstract import Electrical
from lcapy import log10
from copy import copy
from probe.source import JDS6600, KA3005P


class Base(Electrical()):
    device = ''

    def willMount(self, device=''):
        """
        device -- URL Example: jds6600:/dev/tty.usbDevice_1:CH1
        """
        pass

    def part_spice(self, *args, **kwargs):
        part = self.mods['flow'][0]
        kwargs['ref'] = self.ref = 'V' + part + self.props.get('ref', self.ref)
        block = Build(part).spice(*args, **kwargs)

        return block

    def __mod__(self, other):
        """Decibels

        Arguments:
            other {Signal} -- the signal compared with

        Returns:
            [float] -- Compared the relative amplitudes in dB of two Signals
        """
        return 20 * log10(other.amplitude / self.amplitude)

    def set_device(self):
        # self.device = 'protocol:/dev/tty.port:CH1'
        protocol, port, channel = self.device.split(':')
        flow = self.mods['flow']
        flow = flow if type(flow) == str else flow[0]
        args = self.get_spice_arguments()
        device = None

        if protocol == 'jds6600':
            device = JDS6600(port=port)
        else:
            device = KA3005P(port=port)

        if hasattr(device, flow):
            generator = getattr(device, flow)
            generator(
                channel=channel or 1,
                **args)

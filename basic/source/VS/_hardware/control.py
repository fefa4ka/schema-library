from .source import JDS6600, KA3005P

class Modificator:
    device = ''

    def willMount(self, device=''):
        """
        device -- URL Example: jds6600:/dev/tty.usbDevice_1:CH1
        """
        pass

    def devices(self):
        if 'SINEV' in self.mods['flow'] or 'PULSEV' in self.mods['flow']:
            return {
                'jds6600': {
                    'title': 'Signal Generator',
                    'port': 'serial',
                    'channels': ['CH1', 'CH2']
                }
            }

        if 'V' in self.mods['flow']:
           return {
                'ka3005d': {
                    'title': 'Laboratory Power Supply',
                    'port': 'serial',
                    'channels': []
                }
            }

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

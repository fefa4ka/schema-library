from . import get_arg_units
from bem import u, u_V, u_Hz, u_s, u_A

class Device:
    name = ''
    serial_number = ''
    waveforms = {}
    channels = 2

class JDS6600(Device):
    channels = 2
    device = None

    def __init__(self, port):
        from .driver.jds6600 import jds6600

        self.device = jds6600(port)

    @property 
    def name(self):
        return self.device.getinfo_devicetype()
    
    @property
    def serial_number(self):
        return self.device.getinfo_serialnumber()
    
    @property
    def channels(self):
        channels_status = {}
        
        for ch in (1,2):
            channel = {
                'waveform': self.device.getwaveform(ch),
                'frequency': self.device.getfrequency(ch),
                'amplitude': self.device.getamplitude(ch),
                'offset': self.device.getoffset(ch),
                'duty_cycle': self.device.getdutycycle(ch)
            }
            channels_status[ch] = channel

        return {
            'status': self.device.getchannelenable(),
            'channels': channels_status,
            'phase': self.device.getphase()
        }


    def set_channel(self, channel, waveform='sine', amplitude=5 @ u_V, frequency=100 @ u_Hz, offset=0 @ u_V, duty_cycle=50):
        print(channel, waveform, frequency, amplitude, offset, duty_cycle)
        channel = int(channel)
        self.device.setfrequency(channel, u(frequency))
        self.device.setwaveform(channel, waveform)
        self.device.setamplitude(channel, u(amplitude))
        self.device.setoffset(channel, u(offset))
        self.device.setdutycycle(channel, duty_cycle)

    @property
    def waveforms(self):
        waveforms = {}
        simulation = simulation_sources()

        for index, form in self.device.getinfo_waveformlist():
            if form.find('ARBITRARY') != -1:
                continue

            waveforms[form] = {
                'name': form,
                'pins': ['output', 'gnd'],
                'args': {
                    'amplitude': {
                        'value': '',
                        'unit': {
                            'name': 'volt',
                            'suffix': 'V'
                        }
                    },
                    'frequency': {
                        'value': '',
                        'unit': {
                            'name': 'hertz',
                            'suffix': 'Hz'
                        }
                    },
                    'offset': {
                        'value': '',
                        'unit': {
                            'name': 'volt',
                            'suffix': 'v'
                        }
                    },
                    'duty': {
                        'value': '',
                        'unit': {
                            'name': 'number',
                            'suffix': ''
                        }
                    },
                    'phase': {
                        'value': '',
                        'unit': {
                            'name': 'number',
                            'suffix': ''
                        }
                    }
                }
            }

        return waveforms

    def SINEV(self, channel, amplitude, frequency, offset=0 @ u_V):
        self.set_channel(channel, 'sine', amplitude, frequency, offset)

    def PULSEV(self, channel, initial_value, pulsed_value, pulse_width, period, delay_time):
        frequency = (1 / u(period)) @ u_Hz
        offset = (pulsed_value / 2) + initial_value
        amplitude = pulsed_value
        duty_cycle = (u(pulse_width) / u(period)) * 100

        self.set_channel(channel, 'pulse', amplitude, frequency, offset, duty_cycle)

    def EXPV(self, channel, initial_value=0 @ u_V, pulsed_value=5 @ u_V, rise_delay_time=0 @ u_s, rise_time_constant=0.1 @ u_s, fall_delay_time=0.1 @ u_s, fall_time_constant=0.1 @ u_s):
        period = u(rise_time_constant) + u(fall_time_constant)
        frequency = (1 / period) @ u_Hz
        offset = initial_value
        amplitude = pulsed_value
        duty_cycle = (u(rise_time_constant) / period) * 100
        
        self.set_channel(channel, 'exp-rize', amplitude, frequency, offset, duty_cycle)



class KA3005P(Device):
    channels = 1
    device = None

    def __init__(self, port):
        from .driver.ka3005d import KoradSerial

        self.device = KoradSerial(port)
        self.name = self.serial_number = self.device.model

    @property
    def channels(self):
        ch = self.device.channel[0]

        channel = {
            'waveform': 'V',
            'value': ch.output_voltage,
            'current': ch.output_current
        }

        return {
            'status': self.device.status,
            'channels': { 'OUT': channel }
        }


    def set_channel(self, channel, waveform='V', value=0 @ u_V, current = 0 @ u_A):
        """ 200 ms time for channel setting """
        channel = self.device.channels[0]
        channel.voltage = u(value)
        self.device.output.on()

    @property
    def waveforms(self):
        waveforms = {}

        waveforms['V'] = {
            'name': 'V',
            'pins': ['output', 'gnd'],
            'args': {
                'value': {
                    'value': '',
                    'unit': {
                        'name': 'volt',
                        'suffix': 'V'
                    }
                }
            }
        }

        return waveforms

    def V(self, channel, value=0 @ u_V):
        self.set_channel(channel, 'V', value)


def simulation_sources():
    from skidl.libs.pyspice_sklib import pyspice_lib

    sources = []
    for part in pyspice_lib.parts:
        name = getattr(part, 'name', '')
        description = getattr(part, 'description')
        pins = [p.name for p in part.pins]
        if description.lower().find('source') != -1:
            args = {}
            part_type = 'current' if description.lower().find('current') != -1 else 'voltage'

            for arg in list(part.pyspice.get('pos', [])) + list(part.pyspice.get('kw', [])):
                unit = get_arg_units(part, arg)

                if arg in pins:
                    unit = 'network'
                if unit == None:
                    unit = {
                        'name': 'number',
                        'suffix': ''
                    }
                elif unit == 'network':
                    unit = {
                        'name': 'network',
                        'suffix': ''
                    }
                else:
                    unit = {
                        'name': unit._prefixed_unit.unit.unit_name,
                        'suffix': unit._prefixed_unit.unit.unit_suffix
                    }

                args[arg] = {
                    'value': '',
                    'unit': unit
                }

            sources.append({
                'name': name,
                'description': description,
                'pins': pins,
                'args': args
            })
    
    return sources

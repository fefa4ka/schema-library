from PySpice.Unit import u_A, u_V, u_s, u_Hz 

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [{ 'port': port, 'desc': '%s %s' % (desc, hwid)} for port, desc, hwid in ports]

def get_analys_devices():
    import subprocess
    devices = [device.split(' - ') for device in subprocess.getoutput(la + ' --scan').split('\n')[1:]]
    devices = {device[0]: {
        'description': device[1].split(':')[0].strip(),
        'channels': device[1].split(':')[1].strip().split(' ')
    } for device in devices}
    return devices


def get_arg_units(part, arg):
    description = getattr(part, 'description')
    part_type = 'current' if description.lower().find('current') != -1 else 'voltage'

    unit = None
    if arg.find('time') != -1 or arg.find('delay') != -1 or arg in ['pulse_width', 'period', 'duration']:
        unit = u_s
    
    if arg.find('frequency') != -1:
        unit = u_Hz
    
    if arg.find('amplitude') != -1 or arg.find('value') != -1 or arg.find('offset') != -1:
        if part_type == 'current':
            unit = u_A
        else:
            unit = u_V

    return unit

def get_minimum_period(sources):
    period = 0 # Default 100 ms
    min_period = None

    for source in sources:
        for arg in source['args'].keys():
            if arg.find('time') != -1 or arg in ['pulse_width', 'period', 'duration']:
                if source['args'][arg]['value']:
                    time = float(source['args'][arg]['value'])
                    if period < time:
                        period = time

                    if not min_period or min_period > time:
                        min_period = time

            if arg.find('frequency') != -1:
                time = 1 / float(source['args'][arg]['value'])
                if period < time:
                    period = time

                if not min_period or min_period > time:
                    min_period = time

    return period if min_period and period / min_period <= 20 else period / 5 if period else 1

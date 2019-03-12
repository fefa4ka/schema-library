from bem import u, u_Hz, u_MHz, u_kHz, u_ns, u_us, u_ms, u_s
import subprocess
import math
from collections import defaultdict

la = 'sigrok-cli'

timebases = [5 @ u_ns, 10 @ u_ns, 20 @ u_ns, 50 @ u_ns, 100 @ u_ns, 500 @ u_ns, 1 @ u_us, 2 @ u_us, 5 @ u_us, 10 @ u_us, 20 @ u_us, 50 @ u_us, 100 @ u_us, 200 @ u_us, 500 @ u_us, 1 @ u_ms, 2 @ u_ms, 5 @ u_ms, 10 @ u_ms, 20 @ u_ms, 50 @ u_ms, 100 @ u_ms, 200 @ u_ms, 500 @ u_ms, 1 @ u_s, 2 @ u_s, 5 @ u_s, 10 @ u_s, 20 @ u_s, 50 @ u_s ]
rates = [100 @ u_kHz, 200 @ u_kHz, 250 @ u_kHz, 500 @ u_kHz, 1 @ u_MHz, 2 @ u_MHz, 3 @ u_MHz, 4 @ u_MHz, 6 @ u_MHz, 8 @ u_MHz, 12 @ u_MHz, 16 @ u_MHz, 24 @ u_MHz]

class Sigrok:
    def capture(self):
        self.channels = defaultdict(list)
        output = subprocess.getoutput(self.command)

        for line in output.split('\n'):
            unpacked = line.split(':')
            if len(unpacked) == 2:
                ch, data = unpacked
                if data.find('V') != -1:
                    data = data.replace('V', '').strip().split(' ')
                else:
                    data = [int(state) for state in ''.join(data.split(' '))]
                    
                self.channels[ch] += data
    
    def prepare(self):
        desire_samples = int(u(end_time) / u(step_time))

        for ch in channels.keys():
            sample_length = self.time / len(channels[ch])
            last_sample = int(end_time / sample_length)
            skip = int(last_sample / desire_samples)
            channels[ch] = channels[ch][::skip if skip else 1][:desire_samples]

        return channels  


class RigolDS(Sigrok):
    def __init__(self, channel, step_time, end_time):
        sample_rate = 1 / u(step_time)

        timebase = '500us'
        for index, time in enumerate(timebases):
            step = u(time) / 50
            current_time = time
            if index == len(timebases) - 1:
                timebase = current_time
                break
            
            next_time = timebases[index + 1] 
            next_step = u(next_time) / 50
            if (u(step_time) >= step and next_step >= u(step_time)) or (u(step_time) <= step and index == 0):
                timebase = current_time if abs(next_step - u(step_time)) > abs(step - u(step_time)) else next_time
                break

        device_step_time = timebase
        frames = math.ceil(((u(end_time) * 1.5) / (u(timebase) / 50)) / 600)
        self.time = frames * u(timebase) * 12

        self.command = la + ' -d rigol-ds -c timebase=' + str(timebase).replace(' ', '').replace('μ', 'u') + ' --channels ' + channel + ' --frames ' + str(frames)
        
                  
class LogicAnalyzer(Sigrok):
    def __init__(self, channel, step_time, end_time):
        sample_rate = 1 / u(step_time)

        for index, rate in enumerate(rates):
            rate = u(rate)
            if (index == len(rates) - 1):
                sample_rate = rate
                break

            next_rate = u(rates[index + 1])
            if (sample_rate >= rate and next_rate >= sample_rate) or (sample_rate <= rate and index == 0): 
                sample_rate = rate if abs(next_rate - sample_rate) > abs(rate - sample_rate) else next_rate
                break

        self.samples = u(end_time) * sample_rate * 1.5
        
        self.time = samples / sample_rate
        self.command = la + ' -d fx2lafw -c samplerate=' + str(int(sample_rate)) + ' --channels ' + channel + ' --samples ' + str(int(samples)) 




def get_sigrok_samples(device, channel, step_time=0.001 @ u_s, end_time=0.2 @ u_s): # samplerate, samples):
    Device = None

    if device.find('fx2lafw') != -1 or device == 'demo':
        Device = LogicAnalyzer(channel, step_time, end_time)
    
    if device.find('rigol-ds') != -1:
        Device = RigolDS(channel, step_time, end_time)

    Device.capture()
     
    return Device.prepare()
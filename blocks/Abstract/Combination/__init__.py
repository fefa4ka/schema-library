from bem import Block
from bem.model import Param
import numpy as np
from PySpice.Unit import SiUnits
import inspect

class Base(Block):
    increase = True
    
    @property
    def values(self):
        values = []
        si_units = inspect.getmembers(SiUnits, lambda a: not (inspect.isroutine(a)))
        prefixes = {prefix[1].__prefix__: prefix[1].__power__ for prefix in si_units if hasattr(prefix[1], '__prefix__')}
        prefixes['u'] = prefixes['μ']
        prefixes['0'] = 0
        
        for part in self.available_parts:
            part_params = [entry.value for entry in part.params.where(Param.name == 'value')]
            for value in part_params:
                values_range = value.split('/')
                if len(values_range) > 1:
                    scales, exponenta = values_range
                    for exp in exponenta.split(' '):
                        exp_unit = self.value.clone()
                        exp_unit._value = pow(10, prefixes.get(exp, None) or int(exp))

                        scale = np.array(scales.split(' ')).astype(int)
                        
                        values += list(scale * exp_unit)
                else:
                    values += value.split(' ')

        
        return values

    def values_optimal(self, desire, error=10):
        return [desire]
        # TODO: make better
        closest = self.value_closest(desire)

        closest_value = closest.value * closest.scale
        value = desire.value * desire.scale
        
        max_error = value * error / 100
        diff = value - closest_value

        values = []
        if max_error > abs(diff):
            values = [closest]
        else:
            diff_unit = desire.clone()

            if (diff > 0 and self.increase) or (diff < 0 and not self.increase):
                values = [closest]

                diff_unit._value = diff

                diff_closest = self.values_optimal(diff_unit)

                values += diff_closest
            else:
                diff_unit._value = diff * 2
                first_closest = self.value_closest(diff_unit)
                first_value = first_closest.value * first_closest.scale 
                second_value = diff * first_value / (diff - first_value)
                diff_unit._value = abs(second_value)
                second_closest = self.value_closest(diff_unit)

                values.append([first_closest, second_closest])

        return values
    
    def value_closest(self, value):
        absolute_value = value.value * value.scale

        closest = None
        for unit in self.values:            
            if not closest:
                closest = unit

            unit_value = unit.value * unit.scale
            closest_value = closest.value * closest.scale
            
            diff_unit = abs(absolute_value - unit_value)
            diff_closest = abs(absolute_value - closest_value)

            if diff_closest > diff_unit:
                closest = unit

        return closest

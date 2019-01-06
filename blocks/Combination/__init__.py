from bem import Block

class Base(Block):
    increase = True
    
    @property
    def values(self):
        values = []
        for part in self.available_parts:
            values += part['values']

        return values

    def values_optimal(self, desire, error=10):
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

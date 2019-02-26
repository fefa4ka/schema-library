from settings import params_tolerance


def u(unit):
    """Absolute float value of PySpice.Unit
    """

    return float(unit.convert_to_power())


def label_prepare(text):
    last_dash = text.rfind('_')
    if last_dash > 0:
        text = text[:last_dash] + '$_{' + text[last_dash + 1:] + '}$'

    return text

def is_tolerated(a, b, tollerance=params_tolerance):
    if type(a) == list and b in a:
        return True

    if type(a) not in [int, float]:
        try:
            a = u(a)
        except:
            pass
   
    if type(b) not in [int, float]:
        try:
            b = u(b)
        except:
            pass

    if b == type(b)(a):
        return True

    try:
        b = float(b)
        a = float(a)
        diff = abs(a - b)
        if diff < a * tollerance:
            return True
    except:
        pass
    
    return False
    

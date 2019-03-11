from bem import Block, u_Ohm, u_V, u_A

class Base(Block):
    """**Voltage Divider**

    Voltage divider from `V_(\i\\n)` to `V_(out)` could be implemented in different ways and provide current `I_(out)`.
    """

    # Props
    V_in = 10 @ u_V
    V_out = 3 @ u_V
    Load = 0.06 @ u_A

    mods = {
        'type': ['resistive']
    }

    def __init__(self, V_in, V_out, Load):
        """
           V_out -- Note that the output voltage is always less than (or equal to) the input voltage; that’s why it’s called a divider.
        """
        
        self.V_in = V_in
        self.V_out = V_out
        self.Load = Load

        self.load(V_in)
        self.circuit()
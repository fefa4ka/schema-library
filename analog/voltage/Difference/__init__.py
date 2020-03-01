from bem.abstract import Electrical, Network


class Base(Electrical(), Network(port='two')):
    """
    The differential amplifier shown here is a device that compares two separate input signals, takes the difference between them, and then amplifies this difference. In the ideal case the output is entirely independent of the individual signal levels – only the difference matters. The differential amplifier is sometimes called a “long-tailed pair.”

    To understand how the circuit works, treat both transistors as identical, and then notice that both transistors are set in the common-emitter configuration. 

    Differential amplifiers are important in applications in which weak signals are contaminated by “pickup” and other miscellaneous noise.

    When both inputs change levels together, that’s a _common-mode_ input change. A differential change is called _normal mode_, or sometimes _differential mode_.

    * Paul Horowitz and Winfield Hill. "2.3.8 Differential amplifier" The Art of Electronics – 3rd Edition. Cambridge University Press, 2015, pp. 102-104
    """
    mods = {
        'via': ['bipolar']
    }
  

# from bem.analog.voltage import Difference
# from bem import u_V, u_Ω, u_A

# opamps = OpAmp(units=3)(V=10)
# Difference(via='opamp', unit=opamps.A)(
# 	V = 10 @ u_V,
# 	Load = 1000 @ u_Ω,
# 	V_ref = 10 @ u_V,
# 	V_gnd = -10 @ u_V,
# 	I_quiescent = 0.0001 @ u_A
# )

from bem import u_V
from bem.tester import Test

class Case(Test):
    def sources(self):
        sources = super().sources()[:]
        sources[0]['args']['amplitude']['value'] = 25

        return sources

    def conditions(self, probes):
        block = self.block
        V_input = (probes['V_input'] @ u_V).canonise()
        V_output = (probes['V_output'] @ u_V).canonise()

        if V_input >= block.V_out and is_tolerated(V_output, block.V_out) == False:
            return 'V_out should be near %s, but %s' % (str(block.V_out), str(V_output))
        
         
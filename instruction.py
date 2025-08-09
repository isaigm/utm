from config import SAME
class Instruction:
    def __init__(self):
        self.p_state = None
        self.q_state = []
        self.input_symbols = []
        self.output_symbols = []
        self.is_while = False
        self.same_end_state = False
        self.same_output_symbol = False
        self.op = None
      
    def __str__(self): 
        q_state_str = SAME if self.same_end_state else self.q_state
        output_symbols_str = SAME if self.same_output_symbol else self.output_symbols
        prefix = "W" if self.is_while else ""
        return f"{prefix}({self.p_state}, {q_state_str}, {self.input_symbols}, {output_symbols_str}, {self.op})"

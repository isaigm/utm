from typing import List, Tuple, Optional
from instruction import Instruction
from config import *
import sys

class MTU:
    def __init__(self, user_input: str = None):
        self.instructions : List[Instruction] = []
        self.initial_user_input: Optional[str] = user_input
        self.program_loaded: bool = False
        self.error_message: Optional[str] = None
        self.states: List[str] = ['00'] 
        self.pointer: int = 1
        self.current_state: str = '00'
        self.accepting_states: List[str] = []
        self.OPERATIONS = {
        ">": self.next,
        "<": self.prev,
        "!": self.nop
        }
        self.job_tape: List[str] = [] 
        self.reset() 

    def reset(self):
        # --- CAMBIO: Volvemos a la lógica de reseteo original y limpia ---
        # El crecimiento dinámico hace que los colchones sean innecesarios.
        current_input_str = self.initial_user_input if self.initial_user_input is not None else ""
        self.job_tape = [symbol for symbol in current_input_str]
        
        # Asegura que siempre haya un 'B' al principio
        if not self.job_tape or self.job_tape[0] != 'B':
            self.job_tape.insert(0, 'B')
        
        # Asegura que siempre haya un 'B' al final
        if len(self.job_tape) == 1 or self.job_tape[-1] != 'B': 
            self.job_tape.append('B')
        
        self.pointer = 1 
        if not current_input_str and len(self.job_tape) < 3:
            self.job_tape = ['B', 'B', 'B'] 
            self.pointer = 1
        self.current_state = '00'

    def read_file(self, file_path: str):
        self.instructions = []
        self.accepting_states = []
        self.states = ['00'] 
        self.program_loaded = False
        self.error_message = None

        def preproc_str(instruction: str):
            return instruction.replace(' ', '').replace('\n', '')

        def preproc_accepting_states(instruction: str):
            return [state for state in instruction[1:-1].split(',')]

        def is_while(instruction: str):
            return instruction[0].lower() == "w"
        
        def raise_error(tokens: List[object], expected_length: int):
            if len(tokens) != expected_length:
                raise Exception(f"Instrucción, se espera {expected_length} tokens, se tienen {len(tokens)}")

        def tokenize(instruction: str) -> List[str]:
            instruction = instruction[1:-1]
            idx = 0
            token = ''
            tokens = []
            def prep_set(idx: int, symbol: str) -> List[str]: 
                cnt = 0
                result_set = []
                tok = ''
                special_symbols = {"BRACE": {"open": '{', "closed": '}'}, "BRACKET": {"open": '[', "closed": ']'}}
                while idx < len(instruction) and cnt >= 0:
                    ch = instruction[idx]
                    if ch == ',':
                        result_set.append(tok)
                        tok = ''
                    elif ch == special_symbols[symbol]["open"]:
                        cnt += 1
                    elif ch == special_symbols[symbol]["closed"]:
                        result_set.append(tok)
                        cnt -= 1
                        break
                    else:
                        tok += ch
                    idx += 1
                if cnt < 0:
                    raise Exception("Sintaxis invalida")
                
                return result_set, idx
          
            while idx < len(instruction):
                curr_ch = instruction[idx]
                if curr_ch == ',':
                    if len(token) > 0: 
                        tokens.append(token)
                    token = ''
                elif curr_ch == '{':
                    result_set, idx = prep_set(idx, "BRACE")
                    tokens.append(result_set)
                elif curr_ch == '[':
                    result_set, idx = prep_set(idx, "BRACKET")
                    tokens.append(result_set)
                else:
                    token += curr_ch
                idx += 1
            if len(token) > 0: 
                tokens.append(token)
            return tokens
        
        with open(file_path, 'r') as file:
            raw_instructions = [preproc_str(raw_str) for raw_str in ''.join(file.readlines()).split('.') if raw_str.strip()]
            try:
                self.accepting_states = preproc_accepting_states(raw_instructions[0])
            except Exception as e:
                print(e)
                print("Saliendo...")
                sys.exit(1)
            for i in range(1, len(raw_instructions)):
                instruction = raw_instructions[i]
                new_instruction = Instruction()
                if is_while(instruction):
                    tokens = tokenize(instruction[1:])
                    raise_error(tokens, 5)
                    new_instruction.is_while = True
                else:
                    tokens = tokenize(instruction)
                    raise_error(tokens, 5)
                new_instruction.p_state = tokens[P_STATE]
                new_instruction.input_symbols =  tokens[INPUT_SYMBOL] if isinstance(tokens[INPUT_SYMBOL], list) else [tokens[INPUT_SYMBOL]]
                if tokens[Q_STATE] == SAME:
                    new_instruction.same_end_state = True
                else:
                    new_instruction.q_state = tokens[Q_STATE] if isinstance(tokens[Q_STATE], list) else [tokens[Q_STATE]]
                if tokens[OUTPUT_SYMBOL] == SAME:
                    new_instruction.same_output_symbol = True
                else:
                    new_instruction.output_symbols = tokens[OUTPUT_SYMBOL] if isinstance(tokens[OUTPUT_SYMBOL], list) else [tokens[OUTPUT_SYMBOL]]
                    
                new_instruction.op = tokens[OPERATION]
                self.instructions.append(new_instruction)
            self.reset()
            self.program_loaded = True
            print(f"Se han cargado {len(self.instructions)} instrucciones")

      
    def next(self):
        self.pointer += 1
        if self.pointer >= len(self.job_tape):
            self.job_tape.append('B')
        
    def prev(self):
        # --- CAMBIO CLAVE: Lógica de crecimiento dinámico a la izquierda ---
        if self.pointer == 0:
            # Si estamos en el borde, creamos espacio a la izquierda
            self.job_tape.insert(0, 'B')
            # El puntero se queda en 0, ahora apuntando a la nueva celda 'B'
        else:
            # Si no estamos en el borde, simplemente nos movemos
            self.pointer -= 1
    
    def nop(self):
        pass
      
    def p_and_s(self, instruction: Instruction) -> bool:
        if not (0 <= self.pointer < len(self.job_tape)):
            return False
        curr_symbol = self.job_tape[self.pointer]
        return self.current_state == instruction.p_state and curr_symbol in instruction.input_symbols

    def write(self, symbol: str):
        if self.pointer < 0: # Esta guarda ahora es teóricamente innecesaria, pero no hace daño
            return 
        while self.pointer >= len(self.job_tape):
            self.job_tape.append('B')
        self.job_tape[self.pointer] = symbol
    
    def read(self) -> str:
        if not (0 <= self.pointer < len(self.job_tape)):
            return 'B' 
        return self.job_tape[self.pointer]
    
    def run_case_1(self, instruction: Instruction): 
        if not instruction.same_output_symbol:
            self.write(instruction.output_symbols[0])
        if not instruction.same_end_state:
            self.current_state = instruction.q_state[0]
    
    def run_case_2(self, instruction: Instruction): 
        self.run_case_1(instruction)

    def run_case_3(self, instruction: Instruction): 
        current_read = self.read()
        try:
            symbol_idx = instruction.input_symbols.index(current_read)
        except ValueError:
            raise Exception(f"Símbolo leído '{current_read}' no encontrado en input_symbols {instruction.input_symbols} para run_case_3.")

        output_symbol = instruction.output_symbols[symbol_idx]
        if output_symbol != SAME:
            self.write(output_symbol)
        if not instruction.same_end_state and instruction.q_state:
             self.current_state = instruction.q_state[0]


    def run_case_4(self, instruction: Instruction):
        current_read = self.read()
        try:
            symbol_idx = instruction.input_symbols.index(current_read)
        except ValueError:
            raise Exception(f"Símbolo leído '{current_read}' no encontrado en input_symbols {instruction.input_symbols} para run_case_4.")
            
        output_state = instruction.q_state[symbol_idx]
        if output_state != SAME:
            self.current_state = output_state
        if not instruction.same_output_symbol:
            self.write(instruction.output_symbols[0])
    
    def run_case_5(self, instruction: Instruction):
        current_read = self.read()
        try:
            symbol_idx = instruction.input_symbols.index(current_read)
        except ValueError:
            raise Exception(f"Símbolo leído '{current_read}' no encontrado en input_symbols {instruction.input_symbols} para run_case_5.")

        output_state = instruction.q_state[symbol_idx]
        output_symbol = instruction.output_symbols[symbol_idx]
        if output_state != SAME:
            self.current_state = output_state
        if output_symbol != SAME:
            self.write(output_symbol)
        
    def do_q_z(self, instruction: Instruction):
        q_len_actual = 0 if instruction.same_end_state else len(instruction.q_state)
        s_len_actual = len(instruction.input_symbols) 
        z_len_actual = 0 if instruction.same_output_symbol else len(instruction.output_symbols)
        if q_len_actual <= 1 and z_len_actual <= 1:
            self.run_case_1(instruction) 
        elif q_len_actual <= 1 and z_len_actual > 1 and z_len_actual == s_len_actual:
            self.run_case_3(instruction)
        elif q_len_actual > 1 and z_len_actual <= 1 and q_len_actual == s_len_actual:
            self.run_case_4(instruction)
        elif q_len_actual > 1 and z_len_actual > 1 and q_len_actual == s_len_actual and z_len_actual == s_len_actual:
            self.run_case_5(instruction)
        else:
            raise Exception(f"Instrucción mal formada o no coincide con ningún caso en do_q_z (q:{q_len_actual}, s:{s_len_actual}, z:{z_len_actual})")

        self.OPERATIONS[instruction.op]()
            
    def run_instruction(self, instruction: Instruction): 
        if instruction.is_while:
            while self.p_and_s(instruction): 
                self.do_q_z(instruction)
                if self.current_state in self.accepting_states:
                    break
        else:
            self.do_q_z(instruction) 
            
    def step(self) -> Tuple[str, Optional[Instruction]]:
        if not self.program_loaded:
            self.error_message = "Ningún programa MTU cargado."
            return "error", None
        if self.error_message and "Error ejecutando" in self.error_message: 
            self.error_message = None
        elif self.error_message: 
            return "error", None 

        if self.current_state in self.accepting_states:
            return "accepted", None

        if not (0 <= self.pointer < len(self.job_tape)):
            self.error_message = f"Puntero ({self.pointer}) fuera de los límites de la cinta ({len(self.job_tape)})."
            return "error", None

        matched_instruction_obj = None
        for instruction in self.instructions:
            if self.p_and_s(instruction): 
                matched_instruction_obj = instruction
                break
        
        if matched_instruction_obj:
            try:
                if matched_instruction_obj.is_while:
                    if self.p_and_s(matched_instruction_obj):
                        self.do_q_z(matched_instruction_obj)
                        if self.current_state in self.accepting_states:
                            return "accepted", matched_instruction_obj
                        return "stepped", matched_instruction_obj
                    else:
                        return "stepped_while_skip", matched_instruction_obj 
                else: 
                    self.do_q_z(matched_instruction_obj)
                    if self.current_state in self.accepting_states:
                        return "accepted", matched_instruction_obj
                    return "stepped", matched_instruction_obj
            except Exception as e_step_exec:
                self.error_message = f"Error ejecutando instrucción {matched_instruction_obj}: {e_step_exec}"
                return "error", matched_instruction_obj
        else:
            return "no_match", None
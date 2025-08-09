import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog
from mtu import MTU
from config import SAME

class MTUVisualizer:
    def __init__(self, mtu: MTU): 
        self.mtu = mtu
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Visualizador de Máquina de Turing Universal (MTU)")
        self.BG_COLOR = (30, 30, 30)
        self.TAPE_CELL_COLOR = (70, 70, 70)
        self.TAPE_TEXT_COLOR = (220, 220, 220)
        self.POINTER_COLOR = (255, 0, 0) # Red
        self.STATE_COLOR = (0, 150, 255)
        self.ACCEPT_STATE_COLOR = (0, 255, 0)
        self.BUTTON_COLOR = (0, 100, 150)
        self.BUTTON_HOVER_COLOR = (0, 150, 200) # Brighter for hover
        self.BUTTON_CLICK_COLOR = (0, 70, 100)  # Darker for click feedback (optional)
        self.BUTTON_TEXT_COLOR = (255, 255, 255)
        self.ERROR_TEXT_COLOR = (255, 100, 100)
        self.INFO_TEXT_COLOR = (200, 200, 200)
        self.font_small = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        self.tape_cell_width = 40
        self.tape_cell_height = 50
        self.tape_y_pos = 100 
        self.buttons = {}
        self.create_buttons()
        self.running = True
        self.clock = pygame.time.Clock()
        self.status_message = "Cargue un programa y una entrada."
        self.last_executed_instruction_str = ""
        self.auto_running = False
        self.auto_run_delay = 100 
        self.last_auto_step_time = 0
        self.active_button_name = None 

    def create_buttons(self):
        btn_width, btn_height = 160, 40
        margin = 20
        start_x = 50
        start_y = self.HEIGHT - btn_height - margin - 50 
        self.buttons["load"] = {"rect": pygame.Rect(start_x, start_y, btn_width, btn_height), "text": "Load Prog.", "action": self.load_program_dialog}
        start_x += btn_width + margin
        self.buttons["input"] = {"rect": pygame.Rect(start_x, start_y, btn_width, btn_height), "text": "Input", "action": self.set_input_dialog}
        start_x += btn_width + margin
        self.buttons["step"] = {"rect": pygame.Rect(start_x, start_y, btn_width // 2, btn_height), "text": "Step", "action": lambda: self.step_mtu(manual_step=True)}
        start_x += btn_width // 2 + margin
        self.buttons["run"] = {"rect": pygame.Rect(start_x, start_y, btn_width // 2, btn_height), "text": "Run", "action": self.toggle_autorun}
        start_x += btn_width // 2 + margin
        self.buttons["stop"] = {"rect": pygame.Rect(start_x, start_y, btn_width // 2, btn_height), "text": "Stop", "action": self.stop_autorun}
        start_x += btn_width // 2 + margin
        self.buttons["reset"] = {"rect": pygame.Rect(start_x, start_y, btn_width // 2, btn_height), "text": "Reset", "action": self.reset_mtu}

    def _show_input_dialog(self, title, prompt):
        root = tk.Tk()
        root.withdraw()
        user_input = simpledialog.askstring(title, prompt, parent=root)
        root.destroy()
        return user_input

    def load_program_dialog(self):
        self.stop_autorun() 
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de programa MTU",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            parent=root
        )
        root.destroy()
        if file_path:
            self.mtu.read_file(file_path) 
            if self.mtu.error_message: 
                self.status_message = f"Error Cargando: {self.mtu.error_message}"
            elif self.mtu.program_loaded: 
                self.status_message = f"Programa '{file_path.split('/')[-1]}' cargado."
                self.last_executed_instruction_str = ""
            else: 
                self.status_message = "Fallo al cargar programa (estado desconocido)."

    def set_input_dialog(self):
        self.stop_autorun()
        new_input = self._show_input_dialog("Entrada de la MTU", "Ingrese la cadena de entrada inicial:")
        if new_input is not None:
            self.mtu.initial_user_input = new_input 
            self.mtu.reset() 
            self.status_message = f"Entrada: '{new_input}'. MTU reseteada."
            self.last_executed_instruction_str = ""

    def step_mtu(self, manual_step=False):
        if manual_step:
            self.stop_autorun() 
        if not self.mtu.program_loaded: 
            self.status_message = "Cargue un programa primero."
            return
        if self.mtu.error_message and "Error Cargando" in self.mtu.error_message:
            self.status_message = f"Corrija el error de carga: {self.mtu.error_message}"
            return
        if self.mtu.error_message and "Error ejecutando" in self.mtu.error_message :
            self.mtu.error_message = None

        status, instruction_obj = self.mtu.step() 
        if instruction_obj:
            q_state_str = SAME if instruction_obj.same_end_state else instruction_obj.q_state
            output_symbols_str = SAME if instruction_obj.same_output_symbol else instruction_obj.output_symbols
            prefix = "W" if instruction_obj.is_while else ""
            self.last_executed_instruction_str = f"{prefix}({instruction_obj.p_state}, {q_state_str}, {instruction_obj.input_symbols}, {output_symbols_str}, {instruction_obj.op})"
        else:
            self.last_executed_instruction_str = "N/A"
        if status == "accepted":
            self.status_message = "¡ACEPTADO!"
            self.stop_autorun()
        elif status == "no_match":
             current_read_sym_for_status = '?'
             if 0 <= self.mtu.pointer < len(self.mtu.job_tape):
                 current_read_sym_for_status = self.mtu.job_tape[self.mtu.pointer]
             self.status_message = f"DETENIDO: No hay coincidencia ({self.mtu.current_state}, '{current_read_sym_for_status}')"
             self.stop_autorun()
        elif status == "error":
            self.status_message = f"ERROR Ejecución: {self.mtu.error_message}" 
            self.stop_autorun()
        elif status == "stepped" or status == "stepped_while_skip": 
            self.status_message = "Paso ejecutado."

    def toggle_autorun(self):
        if not self.mtu.program_loaded:
            self.status_message = "Cargue un programa primero."
            return
        
        if self.mtu.error_message and "Error Cargando" in self.mtu.error_message:
            self.status_message = f"Corrija el error de carga: {self.mtu.error_message}"
            return
        is_accepted = self.mtu.current_state in self.mtu.accepting_states
        is_halted_or_error_gui = self.status_message and \
                             ("DETENIDO" in self.status_message.upper() or \
                              "ERROR EJECUCIÓN" in self.status_message.upper())
        is_error_mtu = self.mtu.error_message and "Error ejecutando" in self.mtu.error_message
        if is_accepted or is_halted_or_error_gui or is_error_mtu:
            self.status_message = "Máquina en estado final o error. Resetee para re-ejecutar."
            self.auto_running = False 
            return
        self.auto_running = not self.auto_running
        if self.auto_running:
            self.status_message = "Ejecución automática iniciada..."
            self.last_auto_step_time = pygame.time.get_ticks()
            if not (is_accepted or is_halted_or_error_gui or is_error_mtu):
                 self.step_mtu(manual_step=False) 
        else:
            self.status_message = "Ejecución automática pausada."

    def stop_autorun(self):
        if self.auto_running:
            self.auto_running = False
            is_final_message = self.status_message and \
                               ("ACEPTADO" in self.status_message.upper() or \
                                "ERROR" in self.status_message.upper() or \
                                "DETENIDO" in self.status_message.upper())
            if not is_final_message:
                self.status_message = "Ejecución automática detenida."

    def reset_mtu(self):
        self.stop_autorun()
        self.mtu.reset() 
        self.status_message = "MTU reseteada a estado inicial."
        self.last_executed_instruction_str = ""
        if self.mtu.error_message and "Error ejecutando" in self.mtu.error_message:
            self.mtu.error_message = None

    def draw_tape(self):
        tape_surface = pygame.Surface((self.WIDTH, self.tape_cell_height + 20)) 
        tape_surface.fill(self.BG_COLOR)
        cells_to_show_half = (self.WIDTH // self.tape_cell_width) // 2
        current_pointer = self.mtu.pointer
        if not self.mtu.job_tape : self.mtu.job_tape = ['B','B','B']
        if not (0 <= current_pointer < len(self.mtu.job_tape)):
             current_pointer = min(max(0, current_pointer), len(self.mtu.job_tape) -1)
             if current_pointer < 0 and len(self.mtu.job_tape) > 0: current_pointer = 0
             self.mtu.pointer = current_pointer 
        start_idx = max(0, current_pointer - cells_to_show_half)
        end_idx = min(len(self.mtu.job_tape), start_idx + cells_to_show_half * 2 + 2)
        if end_idx >= len(self.mtu.job_tape) and (end_idx - start_idx) < (cells_to_show_half * 2 + 1):
            start_idx = max(0, len(self.mtu.job_tape) - (cells_to_show_half * 2 + 1))
        screen_x = 0
        for i in range(start_idx, end_idx):
            symbol = 'B' 
            if i < len(self.mtu.job_tape):
                symbol = self.mtu.job_tape[i]
            cell_rect = pygame.Rect(screen_x, 0, self.tape_cell_width, self.tape_cell_height)
            pygame.draw.rect(tape_surface, self.TAPE_CELL_COLOR, cell_rect) 
            pygame.draw.rect(tape_surface, self.TAPE_TEXT_COLOR, cell_rect, 1) 
            symbol_text = self.font_medium.render(str(symbol), True, self.TAPE_TEXT_COLOR)
            text_rect = symbol_text.get_rect(center=cell_rect.center)
            tape_surface.blit(symbol_text, text_rect)
            if i == current_pointer:
                ptr_points = [
                    (cell_rect.centerx, cell_rect.bottom + 5), 
                    (cell_rect.centerx - 7, cell_rect.bottom + 15), 
                    (cell_rect.centerx + 7, cell_rect.bottom + 15), 
                ]
                pygame.draw.polygon(tape_surface, self.POINTER_COLOR, ptr_points)
            screen_x += self.tape_cell_width
        self.screen.blit(tape_surface, (0, self.tape_y_pos))

    def draw_state_and_info(self):
        current_state_y_pos = self.tape_y_pos + self.tape_cell_height + 40
        state_text_str = f"Estado: {self.mtu.current_state}"
        state_color = self.STATE_COLOR
        if self.mtu.current_state in self.mtu.accepting_states:
            state_color = self.ACCEPT_STATE_COLOR
            state_text_str += " (Aceptación)"
        state_surf = self.font_large.render(state_text_str, True, state_color)
        state_rect_bg = state_surf.get_rect(centerx=self.WIDTH // 2, y=current_state_y_pos)
        state_rect_bg.inflate_ip(20,10) 
        pygame.draw.rect(self.screen, self.BG_COLOR, state_rect_bg) 
        pygame.draw.rect(self.screen, state_color, state_rect_bg, 2) 
        text_rect = state_surf.get_rect(center=state_rect_bg.center)
        self.screen.blit(state_surf, text_rect)
        
        status_color = self.INFO_TEXT_COLOR
        effective_status_message = self.status_message
        if self.mtu.error_message and "ERROR" in self.status_message.upper():
            effective_status_message = self.status_message 
        elif self.mtu.error_message: 
            effective_status_message = f"ERROR MTU: {self.mtu.error_message}"
        current_status_upper = effective_status_message.upper() 
        if "ERROR" in current_status_upper:
            status_color = self.ERROR_TEXT_COLOR
        elif "ACEPTADO" in current_status_upper:
            status_color = self.ACCEPT_STATE_COLOR
        status_surf = self.font_medium.render(effective_status_message, True, status_color)
        status_rect = status_surf.get_rect(centerx=self.WIDTH // 2, y=state_rect_bg.bottom + 25)
        self.screen.blit(status_surf, status_rect)
        if self.last_executed_instruction_str and self.last_executed_instruction_str != "N/A":
            instr_surf = self.font_small.render(f"Última Instr.: {self.last_executed_instruction_str}", True, self.INFO_TEXT_COLOR)
            instr_rect = instr_surf.get_rect(centerx=self.WIDTH // 2, y=status_rect.bottom + 20)
            self.screen.blit(instr_surf, instr_rect)

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for name, btn in self.buttons.items():
            color = self.BUTTON_COLOR
            if btn["rect"].collidepoint(mouse_pos):
                color = self.BUTTON_HOVER_COLOR
                if self.active_button_name == name: 
                    color = self.BUTTON_CLICK_COLOR
            if name == "run" and self.auto_running: 
                color = (0, 200, 100) 
            pygame.draw.rect(self.screen, color, btn["rect"], border_radius=5) 
            text_surf = self.font_small.render(btn["text"], True, self.BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            self.screen.blit(text_surf, text_rect)

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        self.draw_tape()
        self.draw_state_and_info()
        self.draw_buttons()
        pygame.display.flip()

    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        for btn_name, btn_data in self.buttons.items():
                            if btn_data["rect"].collidepoint(event.pos):
                                self.active_button_name = btn_name
                                break 
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: 
                        if self.active_button_name: 
                            btn_data = self.buttons.get(self.active_button_name)
                            if btn_data and btn_data["rect"].collidepoint(event.pos): 
                                btn_data["action"]()
                        self.active_button_name = None 

            if self.auto_running:
                if current_time - self.last_auto_step_time > self.auto_run_delay:
                    can_step_automatically = True
                    if self.mtu.current_state in self.mtu.accepting_states:
                        can_step_automatically = False
                    
                
                    is_gui_halted_or_error = self.status_message and \
                                             ("DETENIDO" in self.status_message.upper() or \
                                              "ERROR" in self.status_message.upper())
                    is_mtu_error = self.mtu.error_message is not None

                    if is_gui_halted_or_error or is_mtu_error:
                         can_step_automatically = False
                    
                    if can_step_automatically:
                        self.step_mtu(manual_step=False) 
                        self.last_auto_step_time = current_time 
                    else:
                        self.stop_autorun()
            self.draw()
            self.clock.tick(60) 
        pygame.quit()

if __name__ == '__main__':
    mtu_instance = MTU() 
    visualizer = MTUVisualizer(mtu_instance)
    visualizer.run()
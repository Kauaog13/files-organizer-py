# src/gui_app.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading # Para executar a organização em segundo plano
import sys

# Importa as lógicas de outros módulos
from core.organizer_logic import organize_files, execute_moves
from utils.logger_config import setup_logging

class FileOrganizerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Organizer Py")
        master.geometry("700x500") # Define o tamanho inicial da janela
        master.resizable(True, True) # Permite redimensionar

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.categories_config_path = os.path.join(self.base_dir, '..', 'config', 'categories.json')

        self.create_widgets()

        # Configura o logger para a GUI
        # Passa o widget de texto para o handler da GUI
        self.logger = setup_logging(self.base_dir, self.log_text)
        self.logger.info("Aplicação File Organizer Py iniciada.")
        self.logger.info("-" * 40)
        self.logger.info("Selecione a pasta para organizar e clique em 'Iniciar Organização'.")


    def create_widgets(self):
        # Frame principal para organização dos elementos
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Seção de seleção de pasta
        folder_frame = tk.LabelFrame(main_frame, text=" Pasta a Organizar ", padx=10, pady=10)
        folder_frame.pack(fill=tk.X, pady=5)

        self.folder_path_var = tk.StringVar()
        self.folder_path_entry = tk.Entry(folder_frame, textvariable=self.folder_path_var, width=60)
        self.folder_path_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        self.browse_button = tk.Button(folder_frame, text="Procurar Pasta", command=self.browse_folder)
        self.browse_button.pack(side=tk.RIGHT)

        # Seção de botões de ação
        action_frame = tk.Frame(main_frame, pady=5)
        action_frame.pack(fill=tk.X)

        self.start_button = tk.Button(action_frame, text="Iniciar Organização", command=self.start_organization_thread, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        self.cancel_button = tk.Button(action_frame, text="Cancelar", command=self.cancel_organization, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

        # Seção de log/status
        log_frame = tk.LabelFrame(main_frame, text=" Log de Atividade ", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # O handler de log será configurado APÓS a criação do self.log_text

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(os.path.normpath(folder_selected))
            self.start_button.config(state=tk.NORMAL) # Habilita o botão Iniciar
            self.logger.info(f"Pasta selecionada: {folder_selected}")
        else:
            self.logger.info("Nenhuma pasta selecionada.")
            self.start_button.config(state=tk.DISABLED)

    def start_organization_thread(self):
        # Desabilita botões para evitar cliques múltiplos
        self.start_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL) # Habilita o botão Cancelar

        # Limpa o log de atividade anterior
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        self.logger.info("Iniciando processo de organização em segundo plano...")
        # Cria uma nova thread para a organização para não travar a GUI
        self.organization_thread = threading.Thread(target=self.run_organization)
        self.organization_thread.start()

    def run_organization(self):
        source_folder = self.folder_path_var.get()
        if not source_folder:
            self.logger.error("Nenhuma pasta selecionada para organizar.")
            self.reset_buttons()
            return

        self.logger.info(f"Analisando arquivos na pasta: {source_folder}")
        result_analysis = organize_files(source_folder, self.categories_config_path)

        if result_analysis["status"] == "error":
            messagebox.showerror("Erro de Análise", result_analysis["message"])
            self.reset_buttons()
            return
        elif result_analysis["status"] == "info": # Nenhum arquivo para organizar
            messagebox.showinfo("Organização Concluída", result_analysis["message"])
            self.reset_buttons()
            return

        # Confirmação antes de executar os movimentos
        planned_moves = result_analysis["planned_moves"]
        ignored_files = result_analysis["ignored"]
        
        confirmation_message = (
            f"Foram encontrados {len(planned_moves)} arquivo(s) para organizar.\n"
            f"Serão ignorados {ignored_files} item(s) (pastas/ocultos).\n\n"
            "Deseja prosseguir com a organização?"
        )
        
        confirm = messagebox.askyesno("Confirmar Organização", confirmation_message)

        if confirm:
            self.logger.info("Confirmação recebida. Executando movimentos...")
            result_execution = execute_moves(planned_moves)
            
            final_message = (
                f"Organização Concluída!\n\n"
                f"Arquivos Movidos: {result_execution['moved']}\n"
                f"Arquivos com Erro: {result_execution['errors']}\n"
                f"Itens Ignorados: {ignored_files}"
            )
            messagebox.showinfo("Organização Concluída", final_message)
            self.logger.info(final_message)
        else:
            self.logger.info("Organização cancelada pelo usuário.")
            messagebox.showinfo("Organização Cancelada", "A organização foi cancelada.")

        self.reset_buttons() # Reabilita botões no final da execução

    def cancel_organization(self):
        # A implementação de um cancelamento real (interrupção da thread) é mais complexa.
        # Por enquanto, apenas desabilita o botão e notifica.
        self.logger.warning("Solicitação de cancelamento. A organização pode levar um tempo para parar.")
        messagebox.showinfo("Cancelamento", "O cancelamento é limitado no momento. Por favor, aguarde a conclusão da operação atual ou feche o aplicativo.")
        self.reset_buttons() # Reabilita os botões

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL if self.folder_path_var.get() else tk.DISABLED)
        self.browse_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

# Ponto de entrada da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
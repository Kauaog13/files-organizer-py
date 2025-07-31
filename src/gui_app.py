# src/gui_app.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import threading
import json
import logging

# Importa as lógicas de outros módulos
from core.organizer_logic import organize_files, execute_moves
from utils.logger_config import setup_logging
from utils.path_utils import get_resource_path # Importa a nova utilidade de caminho

# --- Caminho para as configurações do aplicativo ---
# Usa get_resource_path para garantir que o caminho funcione no executável
APP_SETTINGS_PATH = get_resource_path('config/app_settings.json')


class FileOrganizerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Organizer Py")
        master.geometry("800x600")
        master.resizable(True, True)

        # BASE_DIR agora é apenas para logger_config
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) 
        # Categoria config path também usará get_resource_path
        self.categories_config_path = get_resource_path('config/categories.json')
        self.app_settings_path = APP_SETTINGS_PATH

        self.create_widgets()

        # Configura o logger para a GUI, passando o widget de texto
        self.logger, self.gui_log_handler = setup_logging(self.base_dir, self.log_text)
        self.logger.info("Aplicação File Organizer Py iniciada.")
        self.logger.info("-" * 40)
        
        self.load_app_settings()
        self.logger.info("Selecione a pasta para organizar e clique em 'Iniciar Organização'.")

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


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

        # Seção de log level e barra de progresso
        options_frame = tk.Frame(main_frame, pady=5)
        options_frame.pack(fill=tk.X)

        # Controle de Nível de Log na GUI
        tk.Label(options_frame, text="Nível de Log:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_level_var = tk.StringVar(value="INFO") # Nível padrão
        self.log_level_combobox = ttk.Combobox(options_frame, textvariable=self.log_level_var,
                                               values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly")
        self.log_level_combobox.pack(side=tk.LEFT, padx=(0, 15))
        self.log_level_combobox.bind("<<ComboboxSelected>>", self.change_gui_log_level)

        # Barra de Progresso
        self.progress_bar = ttk.Progressbar(options_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.progress_label = tk.Label(options_frame, text="0/0")
        self.progress_label.pack(side=tk.LEFT)

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

    def change_gui_log_level(self, event=None):
        """Altera o nível de log exibido na GUI com base na seleção do combobox."""
        selected_level_str = self.log_level_var.get()
        log_level = getattr(logging, selected_level_str, logging.INFO)
        if self.gui_log_handler:
            self.gui_log_handler.setLevel(log_level)
            self.logger.info(f"Nível de log da GUI alterado para: {selected_level_str}")
        else:
            self.logger.warning("Handler de log da GUI não encontrado para alterar o nível.")


    def load_app_settings(self):
        """Carrega as configurações do aplicativo, incluindo a última pasta usada."""
        try:
            with open(self.app_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            last_folder = settings.get("last_folder", "")
            if os.path.isdir(last_folder):
                self.folder_path_var.set(last_folder)
                self.start_button.config(state=tk.NORMAL)
                self.logger.info(f"Última pasta utilizada carregada: '{last_folder}'")
            else:
                self.logger.info("Última pasta utilizada não encontrada ou inválida.")
        except FileNotFoundError:
            self.logger.warning(f"Arquivo de configurações do app '{self.app_settings_path}' não encontrado. Criando um novo.")
            self.save_app_settings("")
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao ler arquivo de configurações do app '{self.app_settings_path}'. Reiniciando configurações.")
            self.save_app_settings("")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar configurações do app: {e}")

    def save_app_settings(self, last_folder_path):
        """Salva as configurações do aplicativo, incluindo a última pasta usada."""
        settings = {"last_folder": last_folder_path}
        try:
            # Garante que a pasta config exista antes de tentar escrever nela
            os.makedirs(os.path.dirname(self.app_settings_path), exist_ok=True) 
            with open(self.app_settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            self.logger.info(f"Configurações do app salvas. Última pasta: '{last_folder_path}'")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações do app: {e}")

    def on_closing(self):
        """Chamado quando a janela é fechada, para salvar configurações."""
        current_folder = self.folder_path_var.get()
        self.save_app_settings(current_folder)
        self.master.destroy()


    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            normalized_path = os.path.normpath(folder_selected)
            self.folder_path_var.set(normalized_path)
            self.start_button.config(state=tk.NORMAL)
            self.logger.info(f"Pasta selecionada: '{normalized_path}'")
        else:
            self.logger.info("Nenhuma pasta selecionada.")
            self.start_button.config(state=tk.DISABLED)

    def start_organization_thread(self):
        # Desabilita botões para evitar cliques múltiplos
        self.start_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        # Limpa o log de atividade anterior na GUI
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Reseta a barra de progresso
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0/0")

        self.logger.info("Iniciando processo de organização em segundo plano...")
        # Cria uma nova thread para a organização para não travar a GUI
        self.organization_thread = threading.Thread(target=self.run_organization)
        self.organization_thread.start()

    def run_organization(self):
        source_folder = self.folder_path_var.get()
        if not source_folder:
            self.logger.error("Nenhuma pasta selecionada para organizar.")
            messagebox.showerror("Erro", "Por favor, selecione uma pasta para organizar.")
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

        # Visualização de Pré-organização (Dry Run Melhorado)
        planned_moves = result_analysis["planned_moves"]
        ignored_files = result_analysis["ignored"]
        
        # --- Abre a janela de pré-organização ---
        confirm_proceed = self.show_pre_organization_dialog(planned_moves, ignored_files)

        if confirm_proceed:
            self.logger.info("Confirmação recebida. Executando movimentos...")
            # Define o total para a barra de progresso
            self.progress_bar['maximum'] = len(planned_moves)

            result_execution = execute_moves(planned_moves, self.update_progress_callback)
            
            final_message = (
                f"Organização Concluída!\n\n"
                f"Arquivos Movidos: {result_execution['moved']}\n"
                f"Arquivos com Erro: {result_execution['errors']}\n"
                f"Itens Ignorados: {ignored_files}"
            )
            messagebox.showinfo("Organização Concluída", final_message)
            self.logger.info(final_message)
            self.save_app_settings(source_folder)
        else:
            self.logger.info("Organização cancelada pelo usuário.")
            messagebox.showinfo("Organização Cancelada", "A organização foi cancelada.")
            self.save_app_settings(self.folder_path_var.get())

        self.reset_buttons()

    def update_progress_callback(self, current, total):
        """Callback para atualizar a barra de progresso e o rótulo."""
        self.master.after(0, self._update_progress_ui, current, total)

    def _update_progress_ui(self, current, total):
        """Função interna para atualizar a UI do progresso na thread principal."""
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"{current}/{total}")


    def show_pre_organization_dialog(self, planned_moves, ignored_files):
        """Mostra uma janela com a lista de arquivos a serem organizados e pede confirmação."""
        dialog = tk.Toplevel(self.master)
        dialog.title("Revisar Organização")
        dialog.geometry("600x450")
        dialog.transient(self.master) # Torna a janela um popup modal
        dialog.grab_set() # Bloqueia a interação com a janela principal

        tk.Label(dialog, text=f"Total de {len(planned_moves)} arquivo(s) planejado(s) para organização.").pack(pady=5)
        tk.Label(dialog, text=f"Serão ignorados {ignored_files} item(s) (pastas/ocultos).").pack()
        tk.Label(dialog, text="Revisar os movimentos propostos:").pack(pady=5)

        # Treeview para exibir os movimentos
        tree_frame = tk.Frame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree = ttk.Treeview(tree_frame, columns=("Original File", "Destination Folder"), show="headings")
        tree.heading("Original File", text="Arquivo Original")
        tree.heading("Destination Folder", text="Pasta de Destino")
        tree.column("Original File", width=250, anchor=tk.W)
        tree.column("Destination Folder", width=250, anchor=tk.W)

        # Adiciona scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill=tk.BOTH, expand=True)

        for move in planned_moves:
            tree.insert("", tk.END, values=(move["arquivo"], move["destino_nome_curto"]))

        # Botões de Confirmação na janela de diálogo
        button_frame = tk.Frame(dialog, pady=10)
        button_frame.pack(pady=5)

        self.dialog_result = False

        def confirm_action():
            self.dialog_result = True
            dialog.destroy()

        def cancel_action():
            self.dialog_result = False
            dialog.destroy()

        confirm_button = tk.Button(button_frame, text="Confirmar e Organizar", command=confirm_action, width=20)
        confirm_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=cancel_action, width=20)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.master.wait_window(dialog)
        return self.dialog_result


    def cancel_organization(self):
        self.logger.warning("Solicitação de cancelamento. A organização pode levar um tempo para parar.")
        messagebox.showinfo("Cancelamento", "O cancelamento é limitado no momento. Por favor, aguarde a conclusão da operação atual ou feche o aplicativo.")
        self.reset_buttons()

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL if self.folder_path_var.get() and os.path.isdir(self.folder_path_var.get()) else tk.DISABLED)
        self.browse_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

# Ponto de entrada da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
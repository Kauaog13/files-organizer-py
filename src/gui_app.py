# src/gui_app.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import json # Importar json para as configurações do app

# Importa as lógicas de outros módulos
from core.organizer_logic import organize_files, execute_moves
from utils.logger_config import setup_logging

# --- Caminho para as configurações do aplicativo ---
# Obtenha o diretório base do arquivo atual (gui_app.py)
BASE_DIR_GUI = os.path.dirname(os.path.abspath(__file__))
APP_SETTINGS_PATH = os.path.join(BASE_DIR_GUI, '..', 'config', 'app_settings.json')


class FileOrganizerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Organizer Py")
        master.geometry("700x500")
        master.resizable(True, True)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.categories_config_path = os.path.join(self.base_dir, '..', 'config', 'categories.json')
        self.app_settings_path = APP_SETTINGS_PATH # Usar o caminho global

        self.create_widgets()

        # Configura o logger para a GUI, passando o widget de texto
        self.logger = setup_logging(self.base_dir, self.log_text)
        self.logger.info("Aplicação File Organizer Py iniciada.")
        self.logger.info("-" * 40)
        
        # Carregar a última pasta ao iniciar
        self.load_app_settings()
        
        self.logger.info("Selecione a pasta para organizar e clique em 'Iniciar Organização'.")

        # Adicionar protocolo de fechamento para salvar configurações
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
        # O handler de log para a GUI é configurado em __init__ após a criação de self.log_text

    def load_app_settings(self):
        """Carrega as configurações do aplicativo, incluindo a última pasta usada."""
        try:
            with open(self.app_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            last_folder = settings.get("last_folder", "")
            if os.path.isdir(last_folder): # Verifica se a pasta ainda existe
                self.folder_path_var.set(last_folder)
                self.start_button.config(state=tk.NORMAL) # Habilita se a pasta for válida
                self.logger.info(f"Última pasta utilizada carregada: '{last_folder}'")
            else:
                self.logger.info("Última pasta utilizada não encontrada ou inválida.")
        except FileNotFoundError:
            self.logger.warning(f"Arquivo de configurações do app '{self.app_settings_path}' não encontrado. Criando um novo.")
            self.save_app_settings("") # Cria o arquivo vazio
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao ler arquivo de configurações do app '{self.app_settings_path}'. Reiniciando configurações.")
            self.save_app_settings("") # Reinicia em caso de erro no JSON
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
        self.master.destroy() # Fecha a janela


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
            self.save_app_settings(source_folder) # Salva a pasta que acabou de ser organizada
        else:
            self.logger.info("Organização cancelada pelo usuário.")
            messagebox.showinfo("Organização Cancelada", "A organização foi cancelada.")
            self.save_app_settings(self.folder_path_var.get()) # Salva a pasta mesmo se cancelar

        self.reset_buttons() # Reabilita botões no final da execução

    def cancel_organization(self):
        # A implementação de um cancelamento real (interrupção da thread) é mais complexa.
        # Por enquanto, apenas desabilita o botão e notifica.
        self.logger.warning("Solicitação de cancelamento. A organização pode levar um tempo para parar.")
        messagebox.showinfo("Cancelamento", "O cancelamento é limitado no momento. Por favor, aguarde a conclusão da operação atual ou feche o aplicativo.")
        self.reset_buttons() # Reabilita os botões

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL if self.folder_path_var.get() and os.path.isdir(self.folder_path_var.get()) else tk.DISABLED)
        self.browse_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

# Ponto de entrada da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
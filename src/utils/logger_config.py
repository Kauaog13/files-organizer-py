import logging
import os
import sys
from datetime import datetime
import tkinter.scrolledtext as scrolledtext
import tkinter as tk # Importar para usar tk.END, tk.NORMAL etc.

class TextWidgetHandler(logging.Handler):
    """
    Um handler de log que envia mensagens para um widget tkinter.scrolledtext.ScrolledText.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state=tk.DISABLED) # Desabilita edição direta pelo usuário

    def emit(self, record):
        msg = self.format(record)
        # Usamos master.after para garantir que a atualização da GUI seja thread-safe
        # e ocorra na thread principal do Tkinter.
        if self.text_widget.winfo_exists(): # Verifica se o widget ainda existe
            # after(0, ...) agenda a função para ser executada na próxima iteração do mainloop
            self.text_widget.after(0, self._update_text_widget, msg)

    def _update_text_widget(self, msg):
        """Função interna para atualizar o widget na thread principal."""
        try:
            self.text_widget.config(state='normal') # Habilita para escrita
            self.text_widget.insert(tk.END, msg + '\n') # Insere a mensagem no final
            self.text_widget.see(tk.END) # Rola para o final
            self.text_widget.config(state='disabled') # Desabilita novamente
        except tk.TclError:
            # Widget pode ter sido destruído enquanto a thread de log tentava atualizar
            pass # Ignora silenciosamente

def setup_logging(base_dir, gui_text_widget=None):
    """
    Configura o sistema de logging do projeto.
    Os logs detalhados serão salvos em um arquivo na pasta 'logs/'.
    Apenas logs de advertência (WARNING) e erros (ERROR/CRITICAL) serão exibidos no console.
    Se um widget de texto da GUI for fornecido, ele também receberá logs.

    Args:
        base_dir (str): O diretório base do script que chama (ex: src/gui_app.py)
                        Usado para derivar o caminho da pasta de logs.
        gui_text_widget (tkinter.scrolledtext.ScrolledText, optional): Widget de texto da GUI para logs.
    """
    logger = logging.getLogger('files_organizer_py') # Dê um nome específico ao seu logger
    logger.setLevel(logging.INFO) # O logger principal deve processar todos os níveis a partir de INFO

    # Limpa handlers existentes para evitar duplicação em múltiplas chamadas (importante para testes ou reconfigurações)
    if (logger.hasHandlers()):
        logger.handlers.clear()

    # Formatter para ambos os handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para arquivo (grava TUDO a partir de INFO)
    # A pasta de logs será relativa ao BASE_DIR do gui_app.py
    logs_dir = os.path.join(base_dir, '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True) # Garante que a pasta de logs exista
    log_filename = datetime.now().strftime("organizer_%Y%m%d_%H%M%S.log")
    log_filepath = os.path.join(logs_dir, log_filename)
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.INFO) # Nível INFO para o arquivo (tudo detalhado)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console (grava apenas WARNING, ERROR, CRITICAL)
    console_handler = logging.StreamHandler(sys.stdout) # sys.stdout para garantir que vá para a saída padrão
    console_handler.setLevel(logging.WARNING) # Nível WARNING para o console (apenas avisos e erros)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para o widget de texto da GUI (se fornecido)
    gui_handler_instance = None # Para retornar a instância
    if gui_text_widget:
        gui_handler_instance = TextWidgetHandler(gui_text_widget)
        gui_handler_instance.setLevel(logging.INFO) # Nível inicial da GUI: INFO (detalhado)
        gui_handler_instance.setFormatter(formatter)
        logger.addHandler(gui_handler_instance)
    
    return logger, gui_handler_instance
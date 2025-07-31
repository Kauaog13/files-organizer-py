import logging
import os
import sys
from datetime import datetime
import tkinter.scrolledtext as scrolledtext
import tkinter as tk # <--- ADICIONE ESTA LINHA!

class TextWidgetHandler(logging.Handler):
    """
    Um handler de log que envia mensagens para um widget tkinter.scrolledtext.ScrolledText.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state=tk.DISABLED) # Usa tk.DISABLED

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL) # Usa tk.NORMAL
        self.text_widget.insert(tk.END, msg + '\n') # Usa tk.END
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED) # Usa tk.DISABLED

def setup_logging(base_dir, gui_text_widget=None):
    """
    Configura o sistema de logging do projeto.
    Os logs detalhados serão salvos em um arquivo na pasta 'logs/'.
    Apenas logs de advertência (WARNING) e erros (ERROR/CRITICAL) serão exibidos no console.
    Se um widget de texto da GUI for fornecido, ele também receberá logs.

    Args:
        base_dir (str): O diretório base do projeto (onde src/ está).
        gui_text_widget (tkinter.scrolledtext.ScrolledText, optional): Widget de texto da GUI para logs.
    """
    logs_dir = os.path.join(base_dir, '..', 'logs')

    os.makedirs(logs_dir, exist_ok=True)

    log_filename = datetime.now().strftime("organizer_%Y%m%d_%H%M%S.log")
    log_filepath = os.path.join(logs_dir, log_filename)

    logger = logging.getLogger('files_organizer_py')
    logger.setLevel(logging.INFO)

    if (logger.hasHandlers()):
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para arquivo (grava TUDO a partir de INFO)
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console (grava apenas WARNING, ERROR, CRITICAL)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para o widget de texto da GUI (se fornecido)
    if gui_text_widget:
        gui_handler = TextWidgetHandler(gui_text_widget)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
    
    return logger
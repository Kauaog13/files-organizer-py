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
        self.text_widget.config(state=tk.NORMAL) # Habilita para escrita
        self.text_widget.insert(tk.END, msg + '\n') # Insere a mensagem no final
        self.text_widget.see(tk.END) # Rola para o final
        self.text_widget.config(state=tk.DISABLED) # Desabilita novamente

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

    # Garante que a pasta de logs exista
    os.makedirs(logs_dir, exist_ok=True)

    # Cria um nome de arquivo de log único com carimbo de data/hora
    log_filename = datetime.now().strftime("organizer_%Y%m%d_%H%M%S.log")
    log_filepath = os.path.join(logs_dir, log_filename)

    # Cria um logger principal para a aplicação
    logger = logging.getLogger('files_organizer_py') # Dê um nome específico ao seu logger
    logger.setLevel(logging.INFO) # O logger principal deve processar todos os níveis a partir de INFO

    # Limpa handlers existentes para evitar duplicação em múltiplas chamadas (importante para testes ou reconfigurações)
    if (logger.hasHandlers()):
        logger.handlers.clear()

    # Formatter para ambos os handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para arquivo (grava TUDO a partir de INFO)
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
    if gui_text_widget:
        gui_handler = TextWidgetHandler(gui_text_widget)
        gui_handler.setLevel(logging.INFO) # A GUI pode receber INFO para mostrar mais detalhes
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
    
    return logger
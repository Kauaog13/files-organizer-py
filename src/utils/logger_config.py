import logging
import os
import sys # Importar sys para o StreamHandler
from datetime import datetime

def setup_logging(base_dir):
    """
    Configura o sistema de logging do projeto.
    Os logs detalhados serão salvos em um arquivo na pasta 'logs/'.
    Apenas logs de advertência (WARNING) e erros (ERROR/CRITICAL) serão exibidos no console.

    Args:
        base_dir (str): O diretório base do projeto (onde src/ está).
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
    
    # Não configure mais via basicConfig, pois estamos usando handlers específicos.
    # logging.basicConfig(...)

    return logger
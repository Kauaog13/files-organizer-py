import os
import sys

def get_resource_path(relative_path):
    """
    Obtém o caminho absoluto para um recurso.
    Funciona tanto para execução em ambiente de desenvolvimento
    quanto para o executável empacotado pelo PyInstaller.

    Args:
        relative_path (str): O caminho do recurso relativo à pasta 'files-organizer-py/'.
                             Ex: 'config/categories.json', 'assets/icon.ico'

    Returns:
        str: O caminho absoluto para o recurso.
    """
    if hasattr(sys, '_MEIPASS'):
        # Se estiver executando como um executável PyInstaller
        # os recursos são extraídos para o diretório temporário _MEIPASS
        # --add-data "config;config" copia a pasta 'config' para a raiz do _MEIPASS
        # então o relative_path já é o correto a partir de _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Se estiver executando como script Python normal (ex: 'python src/gui_app.py')
        # A pasta base é a raiz do projeto 'files-organizer-py/'
        # __file__ está em src/gui_app.py
        # os.path.dirname(__file__) -> src/
        # os.path.abspath(...) -> C:/caminho/para/projeto/src/
        # os.path.join(..., '..') -> C:/caminho/para/projeto/
        return os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), relative_path)
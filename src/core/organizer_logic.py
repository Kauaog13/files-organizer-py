import os
import shutil
import json
import logging

logger = logging.getLogger('files_organizer_py')

# --- Nova Função para Gerar Nome de Arquivo Único ---
def get_unique_filename(destination_path, original_filename):
    """
    Gera um nome de arquivo único adicionando um sufixo numérico se o arquivo já existir.
    Ex: 'foto.jpg' -> 'foto (1).jpg' -> 'foto (2).jpg'
    """
    base, ext = os.path.splitext(original_filename)
    counter = 1
    new_filename = original_filename
    
    # Enquanto o novo caminho completo existir, tenta um novo nome
    while os.path.exists(os.path.join(destination_path, new_filename)):
        new_filename = f"{base} ({counter}){ext}"
        counter += 1
    return new_filename

# --- Nova variável de caminho para o arquivo de exclusão ---
# Usamos os.path.dirname(os.path.abspath(__file__)) para obter o diretório do arquivo atual (organizer_logic.py)
# e então navegar até 'config'
EXCLUDE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'exclude_list.json')

# --- Nova Função para Carregar Exclusões ---
def load_exclusions(config_path):
    """Carrega a lista de arquivos e pastas a serem excluídos do arquivo JSON."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            exclusions = json.load(f)
        logger.info(f"Lista de exclusão carregada de '{config_path}'.")
        return exclusions
    except FileNotFoundError:
        logger.warning(f"Aviso: O arquivo de exclusão '{config_path}' não foi encontrado. Nenhuma exclusão será aplicada.")
        return {"exclude_files": [], "exclude_folders": []} # Retorna vazio se não encontrado
    except json.JSONDecodeError:
        logger.error(f"Erro: O arquivo '{config_path}' não é um JSON válido. Lista de exclusão ignorada.")
        return {"exclude_files": [], "exclude_folders": []}
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar exclusões de '{config_path}': {e}. Lista de exclusão ignorada.")
        return {"exclude_files": [], "exclude_folders": []}

def load_categories(config_path):
    """Carrega as categorias de arquivo do arquivo JSON."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        logger.info(f"Categorias carregadas de '{config_path}'.")
        return categories
    except FileNotFoundError:
        logger.error(f"Erro: O arquivo de configurações de categorias '{config_path}' não foi encontrado.")
        raise # Levanta a exceção para que o chamador (GUI) possa tratá-la
    except json.JSONDecodeError:
        logger.error(f"Erro: O arquivo '{config_path}' não é um JSON válido. Verifique a sintaxe.")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar categorias de '{config_path}': {e}")
        raise

def organize_files(source_folder, categories_config_path):
    """
    Analisa e organiza arquivos em uma pasta.
    Retorna um dicionário com o status da operação.
    """
    if not os.path.isdir(source_folder):
        logger.error(f"Erro: A pasta de origem '{source_folder}' não existe.")
        return {"status": "error", "message": "Pasta de origem não encontrada."}

    logger.info(f"Iniciando análise da pasta: {source_folder}")

    try:
        categorias = load_categories(categories_config_path)
    except Exception:
        return {"status": "error", "message": "Falha ao carregar categorias."}

    categoria_outros = "Outros"
    if categoria_outros not in categorias:
        categorias[categoria_outros] = []

    # Carregar a lista de exclusões
    exclusions = load_exclusions(EXCLUDE_CONFIG_PATH)
    exclude_files_list = [f.lower() for f in exclusions.get("exclude_files", [])]
    exclude_folders_list = [f.lower() for f in exclusions.get("exclude_folders", [])]

    movimentos_planejados = []
    arquivos_ignorados = 0

    for nome_item in os.listdir(source_folder):
        # Verificar se o item está na lista de exclusão de arquivos
        if nome_item.lower() in exclude_files_list:
            logger.info(f"Ignorando arquivo por estar na lista de exclusão: '{nome_item}'")
            arquivos_ignorados += 1
            continue
        
        caminho_completo_item = os.path.join(source_folder, nome_item)

        if os.path.isdir(caminho_completo_item):
            # Verificar se a pasta está na lista de exclusão de pastas
            if nome_item.lower() in exclude_folders_list:
                logger.info(f"Ignorando pasta por estar na lista de exclusão: '{nome_item}'")
                arquivos_ignorados += 1
                continue

            if nome_item in categorias:
                logger.info(f"Ignorando pasta de categoria: '{nome_item}'")
            else:
                logger.info(f"Ignorando pasta: '{nome_item}'")
            arquivos_ignorados += 1
            continue
        
        if nome_item.startswith('.'): # Ignora arquivos ocultos (comuns em sistemas Linux/macOS)
            logger.info(f"Ignorando arquivo oculto: '{nome_item}'")
            arquivos_ignorados += 1
            continue

        if os.path.isfile(caminho_completo_item):
            _, extensao = os.path.splitext(nome_item)
            extensao = extensao.lower()

            pasta_destino_nome = categoria_outros
            encontrado = False
            for categoria, extensoes_lista in categorias.items():
                if extensao in extensoes_lista:
                    pasta_destino_nome = categoria
                    encontrado = True
                    break
            
            caminho_pasta_destino = os.path.join(source_folder, pasta_destino_nome)
            
            movimentos_planejados.append({
                "arquivo": nome_item,
                "origem": caminho_completo_item,
                "destino_pasta": caminho_pasta_destino,
                "destino_nome_curto": pasta_destino_nome
            })
            logger.info(f"  Planejado: '{nome_item}' -> '{pasta_destino_nome}{os.sep}{nome_item}'")
        else:
            logger.info(f"Ignorando item (não é um arquivo nem pasta de categoria): '{nome_item}'")
            arquivos_ignorados += 1

    if not movimentos_planejados:
        logger.info("\nNenhum arquivo elegível para organização foi encontrado.")
        return {"status": "info", "message": "Nenhum arquivo para organizar.", "moved": 0, "errors": 0, "ignored": arquivos_ignorados}
    
    return {"status": "planned", "planned_moves": movimentos_planejados, "ignored": arquivos_ignorados}

def execute_moves(planned_moves):
    """
    Executa os movimentos de arquivo planejados.
    """
    arquivos_movidos = 0
    arquivos_com_erro = 0

    for movimento in planned_moves:
        arquivo = movimento["arquivo"]
        origem = movimento["origem"]
        destino_pasta = movimento["destino_pasta"]
        destino_nome_curto = movimento["destino_nome_curto"]

        # Gerar nome de arquivo único para o destino
        final_filename = get_unique_filename(destino_pasta, arquivo)
        final_destination_path = os.path.join(destino_pasta, final_filename)

        logger.info(f"Executando '{arquivo}' -> '{destino_nome_curto}{os.sep}{final_filename}'...")
        try:
            os.makedirs(destino_pasta, exist_ok=True)
            shutil.move(origem, final_destination_path)
            logger.info(f"  -> Movido com sucesso.")
            arquivos_movidos += 1
        except shutil.Error as e:
            logger.error(f"  !!! ERRO ao mover '{arquivo}'. Motivo: {e}")
            logger.error(f"  (Verifique se o arquivo já existe no destino ou não há permissão.)")
            arquivos_com_erro += 1
        except Exception as e:
            logger.critical(f"  !!! ERRO CRÍTICO INESPERADO ao processar '{arquivo}': {e}")
            arquivos_com_erro += 1
    
    return {"status": "done", "moved": arquivos_movidos, "errors": arquivos_com_erro}
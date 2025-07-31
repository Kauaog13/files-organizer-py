# src/core/organizer_logic.py

import os
import shutil
import json
import logging # Importar logging para usar o logger configurado

# O logger será obtido do módulo de configuração, não configurado aqui
logger = logging.getLogger('files_organizer_py') # Obtém o logger configurado globalmente

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

    movimentos_planejados = []
    arquivos_ignorados = 0

    for nome_item in os.listdir(source_folder):
        caminho_completo_item = os.path.join(source_folder, nome_item)

        if os.path.isdir(caminho_completo_item):
            if nome_item in categorias:
                logger.info(f"Ignorando pasta de categoria: '{nome_item}'")
            else:
                logger.info(f"Ignorando pasta: '{nome_item}'")
            arquivos_ignorados += 1
            continue
        
        if nome_item.startswith('.'):
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

        logger.info(f"Executando '{arquivo}' -> '{destino_nome_curto}{os.sep}{arquivo}'...")
        try:
            os.makedirs(destino_pasta, exist_ok=True)
            shutil.move(origem, destino_pasta)
            logger.info(f"  -> Movido com sucesso.")
            arquivos_movidos += 1
        except shutil.Error as e:
            logger.error(f"  !!! ERRO ao mover '{arquivo}'. Motivo: {e}")
            logger.error(f"  (Verifique se o arquivo já existe no destino ou se há permissões.)")
            arquivos_com_erro += 1
        except Exception as e:
            logger.critical(f"  !!! ERRO CRÍTICO INESPERADO ao processar '{arquivo}': {e}")
            arquivos_com_erro += 1
    
    return {"status": "done", "moved": arquivos_movidos, "errors": arquivos_com_erro}
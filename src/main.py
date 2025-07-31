import os
import shutil
import json
import sys
# Removido: import logging (pois será configurado via util)
# Removido: from datetime import datetime (pois será usado apenas no util de log)

# Importa a função de configuração de log
from utils.logger_config import setup_logging

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_CONFIG_PATH = os.path.join(BASE_DIR, '..', 'config', 'categories.json')

# Configura o logger chamando a função do módulo separado
logger = setup_logging(BASE_DIR)


# --- FUNÇÃO PARA CARREGAR CATEGORIAS ---
def load_categories(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        logger.info(f"Categorias carregadas de '{config_path}'.")
        return categories
    except FileNotFoundError:
        logger.error(f"Erro: O arquivo de configurações de categorias '{config_path}' não foi encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Erro: O arquivo '{config_path}' não é um JSON válido. Verifique a sintaxe.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar categorias de '{config_path}': {e}")
        sys.exit(1)

# Carrega as categorias do arquivo JSON
categorias = load_categories(CATEGORIES_CONFIG_PATH)

categoria_outros = "Outros"
if categoria_outros not in categorias:
    categorias[categoria_outros] = []

logger.info(f"--- Bem-vindo ao files-organizer-py! ---")
logger.info("Categorias configuradas:")
for categoria, extensoes in categorias.items():
    if categoria != categoria_outros:
        logger.info(f"  {categoria}: {', '.join(extensoes)}")
logger.info(f"  Arquivos não categorizados irão para: {categoria_outros}")
logger.info("-" * 40)

# --- 1. SOLICITA A PASTA DE ORIGEM AO USUÁRIO ---
while True:
    pasta_origem_input = input("Digite o caminho completo da pasta que deseja organizar (ou 'sair' para encerrar): ").strip()

    if pasta_origem_input.lower() == 'sair':
        logger.info("Organizador encerrado pelo usuário.")
        sys.exit(0)

    pasta_origem = os.path.normpath(pasta_origem_input)

    if not os.path.isdir(pasta_origem):
        logger.warning(f"Erro: A pasta '{pasta_origem}' não existe ou o caminho está incorreto. Por favor, verifique e tente novamente.")
    else:
        break

logger.info(f"Iniciando análise da pasta: {pasta_origem}")

movimentos_planejados = []
arquivos_ignorados = 0

# --- 2. PERCORRE E ANALISA OS ARQUIVOS NA PASTA DE ORIGEM (FASE DE SIMULAÇÃO) ---
for nome_item in os.listdir(pasta_origem):
    caminho_completo_item = os.path.join(pasta_origem, nome_item)

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
        
        caminho_pasta_destino = os.path.join(pasta_origem, pasta_destino_nome)
        
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

# --- 3. PERGUNTA CONFIRMAÇÃO ANTES DE MOVER ---
if not movimentos_planejados:
    logger.info("\nNenhum arquivo elegível para organização foi encontrado.")
else:
    logger.info(f"\nTotal de {len(movimentos_planejados)} arquivo(s) planejado(s) para organização.")
    confirmacao = input("Deseja prosseguir com a organização? (s/n): ").lower().strip()

    if confirmacao != 's':
        logger.info("Organização cancelada pelo usuário.")
    else:
        logger.info("\nIniciando execução da organização...")
        arquivos_movidos = 0
        arquivos_com_erro = 0

        # --- PROCESSO DE EXECUÇÃO DOS MOVIMENTOS ---
        for movimento in movimentos_planejados:
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

        logger.info("-" * 40)
        logger.info("\n--- ORGANIZAÇÃO CONCLUÍDA! ---")
        logger.info(f"Total de arquivos movidos: {arquivos_movidos}")
        logger.info(f"Total de arquivos com erro: {arquivos_com_erro}")
        
logger.info(f"Total de itens ignorados (pastas, ocultos): {arquivos_ignorados}") 
logger.info(f"Verifique a pasta: {pasta_origem}")
import os
import shutil
import json
import sys # Para usar sys.exit()

# --- CONFIGURAÇÃO ---
# Obtenha o diretório base do script (onde main.py está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho para o arquivo de configurações de categorias
CATEGORIES_CONFIG_PATH = os.path.join(BASE_DIR, '..', 'config', 'categories.json')

# Define a pasta que você quer organizar

# ATENÇÃO: SUBSTITUA ESTE CAMINHO PARA A SUA PASTA REAL!
pasta_origem = r"C:\Users\SeuUser\Área de Trabalho\PastaTeste" # <--- ALTERE AQUI!

# --- FUNÇÃO PARA CARREGAR CATEGORIAS ---
def load_categories(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        return categories
    except FileNotFoundError:
        print(f"Erro: O arquivo de configurações de categorias '{config_path}' não foi encontrado.")
        sys.exit(1) # Sai do script com erro
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{config_path}' não é um JSON válido. Verifique a sintaxe.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao carregar categorias de '{config_path}': {e}")
        sys.exit(1)

# Carrega as categorias do arquivo JSON
categorias = load_categories(CATEGORIES_CONFIG_PATH)

# A categoria para arquivos não listados no JSON
categoria_outros = "Outros"
if categoria_outros not in categorias: # Garante que "Outros" seja uma categoria válida
    categorias[categoria_outros] = [] # Adiciona como uma lista vazia, será o destino padrão

# --- VERIFICAÇÃO INICIAL ---
if not os.path.isdir(pasta_origem):
    print(f"Erro: A pasta '{pasta_origem}' não existe. Verifique o caminho e tente novamente.")
    sys.exit(1) # Sai do script com erro

print(f"--- Iniciando a organização da pasta: {pasta_origem} ---")
print("Categorias configuradas:")
for categoria, extensoes in categorias.items():
    if categoria != categoria_outros: # Não imprime "Outros" com suas extensões (que é vazia)
        print(f"  {categoria}: {', '.join(extensoes)}")
print(f"  Arquivos não categorizados irão para: {categoria_outros}")
print("-" * 40) # Linha divisória

# --- PROCESSO DE ORGANIZAÇÃO ---
arquivos_movidos = 0
arquivos_com_erro = 0
arquivos_ignorados = 0

# Percorre os itens na pasta de origem
for nome_item in os.listdir(pasta_origem):
    caminho_completo_item = os.path.join(pasta_origem, nome_item)

    # Ignora pastas (incluindo as pastas de categoria criadas pelo script) e arquivos ocultos
    if os.path.isdir(caminho_completo_item):
        # Ignora as pastas de destino para evitar loop infinito ou mover pastas erradas
        if nome_item in categorias:
            print(f"Ignorando pasta de categoria: '{nome_item}'")
        else:
            print(f"Ignorando pasta (não é uma pasta de categoria): '{nome_item}'")
        arquivos_ignorados += 1
        continue

    # Ignora arquivos ocultos (que começam com '.') no Linux/macOS
    if nome_item.startswith('.'):
        print(f"Ignorando arquivo oculto: '{nome_item}'")
        arquivos_ignorados += 1
        continue

    # Processa apenas arquivos
    if os.path.isfile(caminho_completo_item):
        _, extensao = os.path.splitext(nome_item)
        extensao = extensao.lower() # Padroniza a extensão para minúsculas

        pasta_destino_nome = categoria_outros # Padrão para "Outros"
        encontrado = False
        for categoria, extensoes_lista in categorias.items():
            if extensao in extensoes_lista:
                pasta_destino_nome = categoria
                encontrado = True
                break # Encontrou a categoria, pode parar de procurar

        if not encontrado and pasta_destino_nome == categoria_outros:
            print(f"Processando '{nome_item}' (Extensão: '{extensao}') -> Não categorizado, irá para '{categoria_outros}'")
        else:
            print(f"Processando '{nome_item}' (Extensão: '{extensao}') -> Categoria: '{pasta_destino_nome}'")

        # Crie o caminho completo da pasta de destino
        caminho_pasta_destino = os.path.join(pasta_origem, pasta_destino_nome)

        try:
            # Crie a pasta de destino se ela não existir
            os.makedirs(caminho_pasta_destino, exist_ok=True)

            # Mova o arquivo
            shutil.move(caminho_completo_item, caminho_pasta_destino)
            print(f"  -> Movido para: '{pasta_destino_nome}{os.sep}{nome_item}'")
            arquivos_movidos += 1
        except shutil.Error as e:
            # Captura erros específicos do shutil, como arquivo já existir no destino
            print(f"  !!! ERRO: Não foi possível mover '{nome_item}'. Motivo: {e}")
            print(f"  (Verifique se o arquivo já existe no destino ou se há permissões.)")
            arquivos_com_erro += 1
        except Exception as e:
            # Captura outros erros inesperados
            print(f"  !!! ERRO INESPERADO ao processar '{nome_item}': {e}")
            arquivos_com_erro += 1
    else:
        print(f"Ignorando item (não é um arquivo nem pasta de categoria): '{nome_item}'")
        arquivos_ignorados += 1


print("-" * 40)
print("\n--- ORGANIZAÇÃO CONCLUÍDA! ---")
print(f"Total de arquivos movidos: {arquivos_movidos}")
print(f"Total de arquivos com erro: {arquivos_com_erro}")
print(f"Total de itens ignorados (pastas, ocultos): {arquivos_ignorados}")
print(f"Verifique a pasta: {pasta_origem}")
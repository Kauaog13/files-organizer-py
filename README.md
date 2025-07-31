# 📁 Files Organizer

Um aplicativo de desktop intuitivo em Python que simplifica a organização de arquivos, **movendo-os automaticamente** para subpastas com base em suas extensões. Ideal para manter sua pasta de Downloads, Área de Trabalho ou qualquer outro diretório sempre **limpo e organizado**.

---

## 🚀 Funcionalidades

- **Interface Gráfica (GUI):** Interação visual e fácil de usar, construída com Tkinter.
  
- **Organização Automatizada:** Move arquivos para subpastas pré-definidas (Imagens, Documentos, Vídeos, etc.).
  
- **Categorias Configuráveis:** As regras de categorização são definidas externamente em config/categories.json, permitindo total personalização.
  
- **Tratamento de Duplicatas:** Renomeia arquivos automaticamente para evitar conflitos de nome no destino (ex: documento.pdf se torna documento (1).pdf).
  
- **Listas de Exclusão:** Ignora arquivos e pastas específicas definidas em config/exclude_list.json, prevenindo a movimentação de itens importantes.
  
- **Salvar Última Pasta:** Lembra e pré-preenche o caminho da última pasta utilizada para maior conveniência do usuário.
  
- **Geração de Logs Detalhados:** Registra todas as operações (arquivos movidos, erros, ignorados) com carimbo de data/hora em arquivos .log na pasta logs/ para rastreabilidade e depuração.
  
- **Controle de Nível de Log na GUI:** Permite ao usuário ajustar o nível de detalhe dos logs exibidos na interface (INFO, WARNING, ERROR).
  
- **Confirmação Antes de Mover:** Apresenta um resumo dos movimentos planejados e solicita confirmação do usuário antes de executar as alterações.
  
- **Barra de Progresso Visual:** Exibe um progresso claro e visual durante a movimentação dos arquivos.
  
- **Visualização de Pré-organização (Dry Run):** Mostra uma lista detalhada dos arquivos e seus destinos propostos em uma janela de revisão antes de confirmar a organização.
  
- **Tratamento de Erros Robusto:** Gerencia situações como pastas não encontradas, arquivos com permissão negada ou erros inesperados.  

---

## 🧠 Como funciona
O aplicativo funciona em três etapas principais:

1. **Seleção e Análise:** O usuário seleciona uma pasta. O aplicativo escaneia esta pasta, identifica os tipos de arquivos com base nas extensões configuradas em config/categories.json e verifica se há arquivos/pastas a serem excluídos (config/exclude_list.json).
   
2. **Revisão e Confirmação:** Uma janela de revisão é exibida, mostrando quais arquivos serão movidos e para onde. O usuário deve confirmar a operação.
   
3. **Execução e Log:** Se confirmado, o aplicativo move os arquivos, tratando duplicatas (renomeando-as) e criando subpastas se necessário. Todo o processo é registrado em tempo real na GUI e em um arquivo de log detalhado na pasta logs/. O progresso é exibido por uma barra visual.  
---

## 🛠️ Tecnologias Utilizadas

- **Python 3.x: Linguagem de programação principal.**
  - os: Para operações de sistema de arquivos (criar pastas, listar diretórios, mover arquivos).
  - shutil: Para operações de arquivo de alto nível (mover arquivos).
  - json: Para ler e escrever arquivos de configuração (categories.json, exclude_list.json, app_settings.json).
  - logging: Para geração de logs detalhados e controle de saída.
  - threading: Para executar a lógica de organização em segundo plano, mantendo a GUI responsiva.
  - Tkinter: Biblioteca padrão do Python para criação da Interface Gráfica do Usuário (GUI).
    
- **PyInstaller:** Ferramenta utilizada para empacotar o aplicativo em um executável standalone (.exe para Windows).
---

# 🧩 Como Utilizar o Files Organizer

Você pode usar o **files-organizer-py** de duas maneiras:

- ✅ **Executando o código-fonte** (ideal para desenvolvedores)
- 📦 **Usando o executável compilado** (ideal para usuários finais)

---

## 👨‍💻 1. Para Desenvolvedores (Executar o Código-Fonte)

Essa opção é ideal se você deseja modificar o código, entender seu funcionamento ou contribuir com o projeto.

### ⚙️ Pré-requisitos

> Apenas necessário para desenvolvedores.

- Python 3.x instalado no sistema
- `pip` para instalar dependências

---

### 🔄 Clone o Repositório

```bash
git clone https://github.com/Kauaog13/files-organizer-py.git
cd files-organizer-py
```

---

### 📦 Instale as Dependências

O projeto utiliza PyInstaller para a compilação:

```bash
pip install -r requirements.txt
```

---

### 🌟 Personalize as Configurações (Opcional)

No diretório **config/**, você pode modificar:

- **categories.json** – Define as categorias de organização por extensão

- **exclude_list.json** – Define arquivos ou extensões a serem ignoradas

> O arquivo **app_settings.json** é gerenciado automaticamente pela aplicação

---

### ▶️ Execute o Aplicativo (GUI)

Abra seu terminal ou prompt de comando na raiz do projeto e execute:
```bash
python src/gui_app.py
```
> A interface gráfica será aberta. Basta seguir as instruções da tela.

---

## 🧑‍💼 2. Para Usuários Finais (Executar o Executável)

Ideal para quem deseja usar o organizador **sem instalar Python** ou lidar com código.

### 📥 Baixar a Última Release

- Acesse a aba **[Releases](https://github.com/Kauaog13/files-organizer-py/releases)** no GitHub.
- Baixe o arquivo `FileOrganizerPy.exe` (ou equivalente para seu sistema operacional) na seção **Assets**.

---

### 🖱️ Executar o Aplicativo

- Após o download, localize o executável no seu computador.
- Dê **duplo clique** no arquivo para abrir.
- Siga as instruções na **interface gráfica** para organizar seus arquivos.

---

## 🛠️ 3. (Opcional) Compilar seu Próprio Executável

Se você quiser criar seu próprio executável, siga os passos abaixo:

### ✅ Requisitos

- Python instalado no sistema
- PyInstaller instalado:

```bash
pip install pyinstaller
```

---

### ⚙️ Compilar

Navegue até a raiz do projeto e execute:
```bash
python -m PyInstaller src/gui_app.py --noconsole --onefile --name "FileOrganizerPy" --add-data "config;config"

```
> O executável será gerado na pasta dist/ com o nome FileOrganizerPy.exe (ou similar, dependendo do seu sistema operacional).

---

# 🧑‍🎓 Autor

Desenvolvido por [Kauã Oliveira](https://github.com/Kauaog13) 🚀  
Contribuições e feedbacks são bem-vindos!

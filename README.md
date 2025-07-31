# 📁 Files Organizer

O **Files Organizer** é uma ferramenta de automação desenvolvida em **Python** que simplifica e acelera o processo de organização de arquivos no seu computador. Ideal para usuários que possuem pastas como "Downloads" constantemente desorganizadas, esta aplicação categoriza e move arquivos automaticamente para subpastas específicas com base em suas **extensões de arquivo**.

---

## 🚀 Funcionalidades

- 🗃️ Detecta automaticamente arquivos em uma pasta de origem
- 📂 Cria subpastas com base nas extensões (ex: `.pdf`, `.jpg`, `.mp4`, etc.)
- 🔁 Move os arquivos para as subpastas correspondentes
- ⚙️ Fácil de configurar e personalizar

---

## 🧠 Como funciona

1. O usuário define o caminho da **pasta de origem** (ex: `Downloads`)
2. O script percorre todos os arquivos dessa pasta
3. Com base nas extensões, ele cria subpastas (caso não existam) e move os arquivos para elas

---

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Módulos padrão da linguagem:
  - `os`
  - `shutil`
  - `pathlib`

---

## 📦 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/seuusuario/files-organizer.git
cd files-organizer
```
### 2. Crie a pasta que será organizada
Crie, por exemplo, uma pasta chamada ParaOrganizar dentro da sua pasta Downloads:  
```
Downloads/  
└── ParaOrganizar/  
```

## 3. Copie o caminho completo dessa pasta
Exemplo (Windows):  
```
C:\Users\SeuNome\Downloads\ParaOrganizar  
```

## 4. Abra o arquivo 'main.py' e altere a variável que define o caminho de origem
No código(Linha 15), procure:  
```
pasta_origem = "CAMINHO/DA/PASTA/AQUI"
```
E substitua pelo caminho copiado.

## 5. Mova arquivos variados para dentro da pasta criada
Ex: imagens, PDFs, músicas, documentos, etc.

## 6. Execute o projeto pelo terminal:
```bash
python main.py
```
Pronto! Seus arquivos serão automaticamente organizados em subpastas baseadas nas extensões 🎯

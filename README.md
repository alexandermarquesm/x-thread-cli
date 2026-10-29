<div align="center">

# ⚡ xthread

**Downloader de alta performance para arquivar threads completas do X (Twitter) com mídias e leitor visual no Linux.**

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey?style=for-the-badge&logo=linux)](https://github.com)
[![uv](https://img.shields.io/badge/Package%20Manager-uv-blueviolet?style=for-the-badge)](https://github.com/astral-sh/uv)
[![Architecture](https://img.shields.io/badge/Architecture-100%25%20Headless%20Async-orange?style=for-the-badge)](https://github.com)

*Zero navegadores abrindo, zero custos de API e com leitor HTML interativo nos estilos **𝕏 Original** e **Steam Classic (2004)**.*

[Instalação](#-instalação) • [Como Usar](#-como-usar) • [Formatos e Leitor HTML](#-leitor-html-exclusivo) • [Comandos](#-comandos-da-cli) • [Licença](#-licença)

</div>

---

## 🌟 Principais Recursos

- 🚀 **100% Headless & Ultra Rápido:** Utiliza requisições GraphQL assíncronas diretas via HTTP. Não abre janelas de Chromium, Selenium ou Firefox na sua tela.
- 🧵 **Reconstrução Inteligente de Narrativa:** Mesmo se você colar o link de um tweet no meio ou no fim da conversa, o motor identifica o tweet raiz e reconstrói a árvore inteira do autor em ordem cronológica (1/N, 2/N, 3/N...).
- 🎨 **Leitor HTML Standalone Dual-View:**
  - **𝕏 Original (Padrão):** Feed idêntico ao do X na web, com linha vertical conectando avatares, selo verificado, citações e ícones SVG oficiais de interação.
  - **🎮 Steam Classic (2004-2008):** Recriação nostálgica e fiel da interface verde militar (VGUI) da Steam antiga, com barra de janelas, tabela de biblioteca, abas e painel de leitura.
- 🌈 **Motor de Temas Integrado:** Alterne instantaneamente entre **Padrão**, **Tokyo Night**, **Dracula**, **Catppuccin Mocha** e **Claro (Daylight)**. A sua preferência fica salva no navegador (`localStorage`).
- 📥 **Download Paralelo de Mídias:** Baixa fotos na resolução máxima original (`:orig`) e vídeos no formato MP4 de maior bitrate com barra de progresso em tempo real no terminal.
- 📑 **Exportação Multiformato:** Salva em **Markdown** (com frontmatter YAML pronto para Obsidian/Notion), **HTML**, **JSON** estruturado e **TXT** limpo.
- 🔒 **Sem API Oficial Paga:** Você não precisa de conta de desenvolvedor do X nem de pagar US$ 100/mês. Basta importar os cookies da sua conta regular uma única vez.

---

## 📥 Instalação

### Opção 1: Usando `uv` (Recomendado — Ultrarrápido e Isolado)

Se você já usa o [uv](https://github.com/astral-sh/uv):

```bash
# Instalar globalmente no seu sistema
uv tool install git+https://github.com/alexandermarquesm/x-thread-cli.git

# Ou clone localmente e instale:
git clone https://github.com/alexandermarquesm/x-thread-cli.git ~/projects/x-thread-cli
cd ~/projects/x-thread-cli
uv tool install . --force
```

### Opção 2: Usando `pipx`

```bash
pipx install git+https://github.com/alexandermarquesm/x-thread-cli.git
```

### Opção 3: Clonando e Executando Manualmente

```bash
git clone https://github.com/alexandermarquesm/x-thread-cli.git
cd x-thread-cli
uv venv
source .venv/bin/activate
uv pip install -e .
```

Após instalado, o comando **`xthread`** estará disponível diretamente em qualquer pasta do seu terminal!

---

## 🔑 Configuração Inicial (Apenas uma vez)

O X exige login para ler threads longas e respostas. Configure a sua sessão em 30 segundos:

```bash
xthread auth
```

1. Abra o [x.com](https://x.com) no seu navegador habitual onde você já está conectado.
2. Pressione **`F12`** para abrir o Inspecionar Elemento.
3. Vá em **Aplicativo (Application)** ou **Armazenamento** -> **Cookies** -> `https://x.com`.
4. Copie os valores de **`auth_token`** e **`ct0`** (ou cole a linha inteira de cookies).

Para testar se a conexão com o X está ativa e válida:
```bash
xthread status
```

---

## 🚀 Como Usar

### Baixar uma thread diretamente
Basta rodar `xthread` seguido da URL do tweet:

```bash
xthread https://x.com/usuario/status/1234567890123456789
```

### Opções comuns

```bash
# 1. Escolher onde salvar
xthread https://x.com/usuario/status/1234567890 -o ~/Downloads/minha_thread

# 2. Exportar todos os formatos (Markdown, HTML, JSON e TXT)
xthread https://x.com/usuario/status/1234567890 -f all

# 3. Baixar apenas o texto (sem salvar imagens/vídeos no disco)
xthread https://x.com/usuario/status/1234567890 --no-media

# 4. Incluir comentários e respostas de outros usuários
xthread https://x.com/usuario/status/1234567890 --all-replies

# 5. Visualizar a thread formatada diretamente no terminal
xthread https://x.com/usuario/status/1234567890 -p

# 6. Definir um limite máximo de tweets na thread
xthread https://x.com/usuario/status/1234567890 -l 50
```

### 📚 Gerenciar e Abrir Threads Salvas

Você pode navegar e visualizar toda a sua coleção salva tanto pelo terminal quanto pelo navegador:

```bash
# Listar todas as threads salvas em uma tabela estilizada no terminal
xthread list

# Filtrar threads por termo ou autor
xthread list -q meianoite

# Abrir a Biblioteca Visual (Dashboard) no navegador
xthread list --open
# ou simplesmente:
xthread open

# Iniciar um servidor web local e abrir http://localhost:8080
xthread serve

# Abrir uma thread específica diretamente no navegador (pelo número # ou autor)
xthread open 1
xthread open meianoite
```

---

## 🎨 Leitor HTML Exclusivo

O arquivo `index.html` gerado para cada thread é totalmente **autônomo** (funciona 100% offline, sem CDNs externas ou scripts pesados).

Na barra superior de controle você pode:
1. **Trocar de Design em 1 clique:**
   - **𝕏 Original:** Visual idêntico ao Twitter/X Web moderno.
   - **🎮 Steam Old:** Recriação pixel-art da clássica interface verde oliva da Valve Steam de 2004.
2. **Alternar Temas de Cores:**
   - 🎨 **Padrão:** Escuro autêntico (Preto puro no X / Verde militar na Steam).
   - 🌃 **Tokyo Night:** Paleta azulada e roxa de desenvolvedor.
   - 🧛 **Dracula:** Clássico tema de alto contraste.
   - ☕ **Catppuccin Mocha:** Tons pastéis confortáveis para leitura prolongada.
   - ☀️ **Claro (Daylight):** Fundo branco limpo para ambientes iluminados.
3. **Salvar em PDF / Imprimir:**
   - Clique no botão `🖨️ PDF` para gerar uma versão limpa para arquivamento ou impressão sem barras laterais.

---

## 🛠️ Comandos da CLI

| Comando | Descrição |
|---|---|
| `xthread <url>` | Baixa e reconstrói a thread da URL informada |
| `xthread download <url> [OPÇÕES]` | Comando explícito com suporte a todas as flags |
| `xthread list` (ou `ls`) | Lista todas as threads salvas no terminal ou abre o hub (`--open`) |
| `xthread open [ALVO]` | Abre uma thread (# ou autor) ou a biblioteca completa no navegador |
| `xthread serve` | Inicia servidor HTTP local (`http://localhost:8080`) para navegar na biblioteca |
| `xthread auth` | Assistente interativo para salvar cookies de sessão |
| `xthread status` | Verifica se os cookies continuam válidos junto ao X |
| `xthread logout` | Remove os cookies e sessões armazenadas localmente |
| `xthread version` | Exibe a versão atual do software |

---

## 📂 Estrutura do Projeto

```
x-thread-cli/
├── pyproject.toml         # Gerenciamento de dependências via uv
├── LICENSE                # Licença MIT
├── README.md              # Documentação completa
└── src/xthread/
    ├── __init__.py        # Exportação de comandos
    ├── cli.py             # Interface de linha de comando com Typer e Rich
    ├── auth.py            # Validação e armazenamento de cookies
    ├── crawler.py         # Motor assíncrono de busca e reconstrução da thread
    ├── downloader.py      # Download paralelo de mídias (fotos originais e vídeos MP4)
    ├── exporter.py        # Gerador dos formatos Markdown, HTML, JSON e TXT
    ├── models.py          # Modelos de dados Pydantic
    └── config.py          # Gerenciamento de configurações e diretórios
```

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.

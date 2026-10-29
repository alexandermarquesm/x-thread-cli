# ⚡ xthread

> **CLI de alta performance para Linux para arquivar e baixar threads completas do X (Twitter).**  
> 100% headless (zero navegadores abrindo), sem custos e sem necessidade de API oficial paga.

---

## 🚀 Destaques

- **Zero Janelas de Navegador:** Utiliza requisições GraphQL assíncronas diretas via HTTP, sem abrir navegadores ou interfaces visuais.
- **Alta Performance:** Construído em Python assíncrono (`httpx` + `asyncio`) com downloads paralelos de mídia controlados por semáforos.
- **Narrativa Reconstruída:** Segue a árvore de respostas do autor original e preserva a ordem cronológica correta (1/N, 2/N, 3/N...).
- **Suporte a Mídias em Qualidade Máxima:** Baixa fotos na resolução original (`:orig`) e vídeos no MP4 de maior bitrate.
- **Múltiplos Formatos de Saída:**
  - **Markdown (`.md`)**: Com frontmatter YAML (perfeito para Obsidian, Notion ou arquivamento).
  - **HTML (`index.html`)**: Leitor moderno em modo escuro (*Reader View*), responsivo e pronto para imprimir/salvar em PDF.
  - **JSON (`.json`)**: Metadados completos estruturados.
  - **Texto (`.txt`)**: Transcrição limpa sem formatação.
- **Comando Global:** Integrado ao seu sistema operacional em `~/.local/bin/xthread`.

---

## 📦 Como Usar

### 1. Autenticação (Apenas uma vez)
Como o X exige login para ler threads e respostas completas, configure sua sessão uma única vez:

```bash
xthread auth
```

O assistente interativo pedirá apenas dois cookies da sua sessão:
1. Abra o `x.com` no seu navegador atual (onde você já está logado).
2. Pressione `F12` (Ferramentas do Desenvolvedor) -> Aba **Aplicativo (Application)** ou **Armazenamento** -> **Cookies** -> `https://x.com`.
3. Copie o valor de **`auth_token`** e **`ct0`** (ou cole o cabeçalho Cookie inteiro).

Pronto! Os cookies ficam salvos de forma segura em `~/.config/xthread/`.

---

### 2. Baixando uma Thread

Basta passar o link ou ID da thread (pode ser o link do primeiro tweet ou de qualquer tweet no meio da conversa):

```bash
xthread https://x.com/usuario/status/1234567890123456789
```

### Exemplos de uso:

#### Salvar em uma pasta específica:
```bash
xthread https://x.com/usuario/status/1234567890 -o ~/Downloads/minha_thread
```

#### Escolher os formatos de saída:
```bash
# Apenas Markdown
xthread https://x.com/usuario/status/1234567890 -f md

# Todos os formatos (Markdown, HTML, JSON, TXT)
xthread https://x.com/usuario/status/1234567890 -f all
```

#### Baixar sem fazer download das fotos/vídeos (mantém links remotos):
```bash
xthread https://x.com/usuario/status/1234567890 --no-media
```

#### Incluir respostas e comentários de outras pessoas:
```bash
xthread https://x.com/usuario/status/1234567890 --all-replies
```

#### Ver pré-visualização no terminal:
```bash
xthread https://x.com/usuario/status/1234567890 -p
```

---

## 🛠️ Comandos Disponíveis

| Comando | Descrição |
|---|---|
| `xthread <url>` | Baixa a thread informada diretamente |
| `xthread auth` | Configura ou atualiza os cookies da sessão |
| `xthread status` | Testa a conexão e verifica a validade da sua sessão |
| `xthread logout` | Apaga os dados de sessão salvos |
| `xthread version` | Exibe a versão do utilitário |

---

## 📁 Estrutura do Projeto

```
~/projects/x-thread-cli/
├── pyproject.toml         # Configuração uv e dependências
├── README.md              # Documentação
└── src/xthread/
    ├── cli.py             # Interface de linha de comando com Typer e Rich
    ├── auth.py            # Gerenciamento de credenciais e status
    ├── crawler.py         # Motor assíncrono de crawling e reconstrução de árvores
    ├── downloader.py      # Download paralelo de fotos e vídeos com barra de progresso
    ├── exporter.py        # Exportadores para Markdown, HTML, JSON e TXT
    ├── models.py          # Modelos de dados com Pydantic
    └── config.py          # Configurações e diretórios do usuário
```

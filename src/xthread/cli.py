"""Rich-powered CLI interface for xthread."""

import asyncio
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from xthread.config import APP_NAME, APP_VERSION, load_config, get_threads_dir
from xthread.auth import add_session, check_auth_status, clear_all_sessions
from xthread.crawler import ThreadCrawler, extract_tweet_id
from xthread.downloader import MediaDownloader
from xthread.exporter import export_markdown, export_json, export_html, export_txt
from xthread.library import scan_saved_threads, generate_library_hub_html

app = typer.Typer(
    name=APP_NAME,
    help="⚡ Baixe threads completas do X (Twitter) em alta performance direto pelo terminal Linux.",
    rich_markup_mode="rich",
    no_args_is_help=False,
)
console = Console()


def render_banner():
    """Print welcoming banner."""
    console.print(
        Panel.fit(
            f"[bold cyan]⚡ {APP_NAME.upper()} v{APP_VERSION}[/bold cyan] - [bold white]Downloader & Biblioteca de Threads do X[/bold white]\n"
            f"[dim]Rápido, silencioso, sem navegador e sem API paga.[/dim]",
            border_style="cyan",
        )
    )


async def execute_download(
    url_or_id: str,
    output: Optional[Path],
    formats: str,
    download_media: bool,
    all_replies: bool,
    preview: bool,
    limit: int,
):
    """Core async routine for downloading threads."""
    cfg = load_config()

    # 1. Check authentication
    status = await check_auth_status()
    if status["accounts_count"] == 0:
        console.print("\n[bold yellow]⚠️ Nenhuma sessão configurada![/bold yellow]")
        console.print(
            "O X exige estar logado para ler respostas e threads completas.\n"
            "Execute [bold cyan]xthread auth[/bold cyan] para configurar seus cookies em 30 segundos.\n"
        )
        raise typer.Exit(code=1)

    try:
        tweet_id = extract_tweet_id(url_or_id)
    except Exception as e:
        console.print(f"[bold red]❌ URL ou ID inválido:[/bold red] {e}")
        raise typer.Exit(code=1)

    with console.status("[bold cyan]Buscando thread no X (GraphQL)...[/bold cyan]", spinner="dots"):
        crawler = ThreadCrawler()
        try:
            thread = await crawler.fetch_thread(
                url_or_id=str(tweet_id),
                include_all_replies=all_replies,
                limit=limit,
            )
        except Exception as e:
            console.print(f"\n[bold red]❌ Falha ao obter a thread:[/bold red] {e}")
            raise typer.Exit(code=1)

    # Summary Panel
    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_row("[bold cyan]Autor:[/bold cyan]", f"{thread.author_name} (@{thread.author_username})")
    summary_table.add_row("[bold cyan]Título:[/bold cyan]", thread.title)
    summary_table.add_row("[bold cyan]Total de Tweets:[/bold cyan]", f"[bold green]{thread.total_tweets}[/bold green]")
    summary_table.add_row("[bold cyan]Métricas:[/bold cyan]", f"❤️ {thread.total_likes:,}  |  🔁 {thread.total_retweets:,}  |  👁️ {thread.total_views:,}")
    summary_table.add_row("[bold cyan]Data Original:[/bold cyan]", thread.created_at.strftime("%d/%m/%Y às %H:%M"))

    console.print()
    console.print(Panel(summary_table, title="[bold green]✓ Thread Localizada[/bold green]", border_style="green"))

    # Determine output directory
    base_dir = Path(cfg.get("default_output_dir", "./threads")).expanduser()
    if output:
        dest_dir = output
    else:
        dest_dir = base_dir / thread.slug

    dest_dir.mkdir(parents=True, exist_ok=True)

    # 2. Download Media if enabled
    total_media_count = sum(len(t.media) for t in thread.tweets)
    if download_media and total_media_count > 0:
        console.print(f"\n[bold cyan]Baixando mídias ({total_media_count} arquivos em paralelo)...[/bold cyan]")
        downloader = MediaDownloader(concurrency=cfg.get("concurrency", 6))
        downloaded = await downloader.download_thread_media(thread, dest_dir, show_progress=True)
        console.print(f"[green]✓ {downloaded}/{total_media_count} mídias salvas com sucesso em: {dest_dir / 'media'}[/green]")
    elif total_media_count > 0:
        console.print(f"[dim]Ignorando download de mídias (--no-media). Links originais mantidos.[/dim]")

    # 3. Export Formats
    format_list = [f.strip().lower() for f in formats.split(",")]
    if "all" in format_list:
        format_list = ["md", "html", "json", "txt"]

    console.print("\n[bold cyan]Exportando arquivos:[/bold cyan]")
    saved_files: list[Path] = []

    for fmt in format_list:
        if fmt in ("md", "markdown"):
            target = dest_dir / "thread.md"
            export_markdown(thread, target)
            saved_files.append(target)
            console.print(f"  [green]• Markdown:[/green] {target}")
        elif fmt == "html":
            target = dest_dir / "index.html"
            export_html(thread, target)
            saved_files.append(target)
            console.print(f"  [green]• HTML (Reader Mode):[/green] {target}")
        elif fmt == "json":
            target = dest_dir / "thread.json"
            export_json(thread, target)
            saved_files.append(target)
            console.print(f"  [green]• JSON estruturado:[/green] {target}")
        elif fmt == "txt":
            target = dest_dir / "thread.txt"
            export_txt(thread, target)
            saved_files.append(target)
            console.print(f"  [green]• Texto simples:[/green] {target}")

    # 4. Automatically update Central Library Hub (threads/index.html)
    try:
        threads_scanned = scan_saved_threads(base_dir)
        hub_path = base_dir / "index.html"
        generate_library_hub_html(threads_scanned, hub_path)
        console.print(f"  [dim]• Biblioteca atualizada:[/dim] [cyan]{hub_path}[/cyan]")
    except Exception:
        pass

    # Optional Live Terminal Preview
    if preview:
        console.print("\n[bold cyan]Pré-visualização da Thread:[/bold cyan]\n")
        for item in thread.tweets:
            badge = f"[bold yellow]#{item.order}[/bold yellow]"
            user_lbl = f"[bold cyan]@{item.author_username}[/bold cyan]"
            time_lbl = f"[dim]{item.created_at_formatted}[/dim]"
            console.print(f"{badge} {user_lbl} • {time_lbl}")
            console.print(f"{item.text}\n")
            if item.media:
                console.print(f"[dim](Contém {len(item.media)} anexo(s) de mídia)[/dim]\n")
            console.print("[dim]" + "─" * 40 + "[/dim]\n")

    console.print(f"\n[bold green]🎉 Concluído com sucesso![/bold green] Arquivos salvos em: [bold]{dest_dir}[/bold]\n")


@app.command(name="download", help="Baixa uma thread completa a partir de uma URL ou ID do tweet.")
def download(
    url: Annotated[str, typer.Argument(help="URL do tweet no X ou ID numérico")],
    output: Annotated[Optional[Path], typer.Option("-o", "--output", help="Diretório de saída")] = None,
    formats: Annotated[str, typer.Option("-f", "--format", help="Formatos (md, html, json, txt, all)")] = "md,html",
    media: Annotated[bool, typer.Option("--media/--no-media", help="Baixar mídias (fotos e vídeos) em alta resolução")] = True,
    all_replies: Annotated[bool, typer.Option("--all-replies", help="Incluir respostas de outros usuários")] = False,
    preview: Annotated[bool, typer.Option("-p", "--preview", help="Exibir pré-visualização da thread no terminal")] = False,
    limit: Annotated[int, typer.Option("-l", "--limit", help="Limite máximo de tweets a carregar")] = 200,
):
    """Download a thread from X."""
    asyncio.run(
        execute_download(
            url_or_id=url,
            output=output,
            formats=formats,
            download_media=media,
            all_replies=all_replies,
            preview=preview,
            limit=limit,
        )
    )


@app.command(name="list", help="Lista e gerencia todas as threads salvas no diretório local.")
def list_threads(
    open_hub: Annotated[bool, typer.Option("-o", "--open", help="Abrir a biblioteca visual no navegador")] = False,
    query: Annotated[Optional[str], typer.Option("-q", "--query", help="Filtrar por autor ou título")] = None,
):
    """List all saved threads in a styled Rich table and update the Library Hub."""
    base_dir = get_threads_dir()

    threads = scan_saved_threads(base_dir)

    # Re-generate library index.html
    hub_path = base_dir / "index.html"
    try:
        generate_library_hub_html(threads, hub_path)
    except Exception:
        pass

    if query:
        q = query.lower()
        threads = [t for t in threads if q in t["title"].lower() or q in t["author_name"].lower() or q in t["author_username"].lower()]

    if not threads:
        console.print(f"\n[bold yellow]Nenhuma thread encontrada em:[/bold yellow] {base_dir}")
        console.print("[dim]Baixe uma thread com: xthread <url>[/dim]\n")
        return

    table = Table(
        title=f"📚 Biblioteca de Threads Salvas ({len(threads)} encontradas)",
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Autor", style="bold white")
    table.add_column("Título", style="cyan")
    table.add_column("Tweets", justify="right", style="green")
    table.add_column("Mídias", justify="right")
    table.add_column("Curtidas", justify="right", style="magenta")
    table.add_column("Data", style="dim")

    for idx, t in enumerate(threads, 1):
        dt_fmt = t["created_at_dt"].strftime("%d/%m/%Y") if t["created_at_dt"] != datetime.min else "Recente"
        table.add_row(
            str(idx),
            f"{t['author_name']} (@{t['author_username']})",
            t["title"][:42] + ("..." if len(t["title"]) > 42 else ""),
            str(t["total_tweets"]),
            f"{t['media_count']} arq." if t["media_count"] > 0 else "-",
            f"❤️ {t['total_likes']:,}",
            dt_fmt,
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]Diretório base:[/dim] [bold]{base_dir}[/bold]")
    console.print(f"[dim]Biblioteca visual:[/dim] [cyan]{hub_path}[/cyan]")
    console.print("[dim]Abra no navegador com: [bold cyan]xthread list --open[/bold cyan] ou [bold cyan]xthread open <#>[/bold cyan]\n[/dim]")

    if open_hub:
        webbrowser.open(f"file://{hub_path.resolve()}")


@app.command(name="ls", hidden=True)
def ls_threads(
    open_hub: Annotated[bool, typer.Option("-o", "--open", help="Abrir a biblioteca visual no navegador")] = False,
    query: Annotated[Optional[str], typer.Option("-q", "--query", help="Filtrar por autor ou título")] = None,
):
    """Alias for list."""
    list_threads(open_hub=open_hub, query=query)


@app.command(name="open", help="Abre uma thread salva ou a biblioteca visual no seu navegador.")
def open_thread(
    target: Annotated[Optional[str], typer.Argument(help="Número da thread (#), parte do nome ou autor (ou vazio para abrir a biblioteca)")] = None,
):
    """Open a saved thread or library hub in browser."""
    base_dir = get_threads_dir()
    threads = scan_saved_threads(base_dir)

    hub_path = base_dir / "index.html"
    try:
        generate_library_hub_html(threads, hub_path)
    except Exception:
        pass

    if not target:
        console.print(f"[bold cyan]Abrindo Biblioteca de Threads no navegador...[/bold cyan]")
        webbrowser.open(f"file://{hub_path.resolve()}")
        return

    # Check if target is a numeric index (1, 2, 3...)
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(threads):
            chosen = threads[idx]
            chosen_html = base_dir / chosen["html_path"]
            console.print(f"[bold green]Abrindo Thread #{target} ({chosen['title'][:35]}...)[/bold green]")
            webbrowser.open(f"file://{chosen_html.resolve()}")
            return
        else:
            console.print(f"[bold red]❌ Índice inválido:[/bold red] escolha um número entre 1 e {len(threads)}")
            return

    # Otherwise search by name
    q = target.lower()
    matches = [t for t in threads if q in t["title"].lower() or q in t["author_username"].lower() or q in t["author_name"].lower()]

    if matches:
        chosen = matches[0]
        chosen_html = base_dir / chosen["html_path"]
        console.print(f"[bold green]Abrindo thread de @{chosen['author_username']}...[/bold green]")
        webbrowser.open(f"file://{chosen_html.resolve()}")
    else:
        console.print(f"[bold red]❌ Nenhuma thread encontrada correspondente a '{target}'.[/bold red]")
        console.print("[dim]Use 'xthread list' para ver todas as threads disponíveis.[/dim]")


@app.command(name="serve", help="Inicia um servidor web local para navegar na biblioteca pelo navegador.")
def serve(
    port: Annotated[int, typer.Option("-p", "--port", help="Porta do servidor local")] = 8080,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Não abrir o navegador automaticamente")] = False,
):
    """Start local web server for the threads library."""
    base_dir = get_threads_dir()
    threads = scan_saved_threads(base_dir)
    hub_path = base_dir / "index.html"
    try:
        generate_library_hub_html(threads, hub_path)
    except Exception:
        pass

    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(base_dir))
    url = f"http://localhost:{port}"

    console.print(f"\n[bold green]⚡ Servidor local iniciado com sucesso![/bold green]")
    console.print(f"[bold cyan]Acesse no seu navegador:[/bold cyan] [underline]{url}[/underline]")
    console.print(f"[dim]Pressione Ctrl+C para encerrar o servidor.[/dim]\n")

    if not no_browser:
        webbrowser.open(url)

    try:
        with ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Servidor encerrado.[/yellow]")


@app.command(name="auth", help="Configura a sua sessão do X (auth_token e ct0) sem abrir navegador.")
def auth():
    """Setup or update X session cookies."""
    render_banner()

    console.print(
        Panel(
            "[bold white]Como obter os cookies da sua conta em 30 segundos:[/bold white]\n\n"
            "1. Abra o [bold cyan]x.com[/bold cyan] no seu navegador (Chrome, Firefox, Brave, Edge, etc.) já conectado.\n"
            "2. Pressione [bold yellow]F12[/bold yellow] para abrir as Ferramentas do Desenvolvedor.\n"
            "3. Vá na aba [bold yellow]Aplicativo (Application)[/bold yellow] ou [bold yellow]Armazenamento (Storage)[/bold yellow] -> [bold yellow]Cookies[/bold yellow] -> [bold cyan]https://x.com[/bold cyan].\n"
            "4. Copie os valores de [bold green]auth_token[/bold green] e [bold green]ct0[/bold green].\n\n"
            "[dim]Dica: Você também pode colar o cabeçalho Cookie completo de qualquer requisição do x.com.[/dim]",
            title="[bold cyan]🔑 Autenticação do X[/bold cyan]",
            border_style="cyan",
        )
    )

    first_input = Prompt.ask("\n[bold cyan]Cole o [bold green]auth_token[/bold green] (ou a string completa de cookies)[/bold cyan]").strip()

    auth_token = None
    ct0 = None
    raw_cookies = None

    if "ct0=" in first_input and "auth_token=" in first_input:
        raw_cookies = first_input
    else:
        auth_token = first_input
        ct0 = Prompt.ask("[bold cyan]Cole o [bold green]ct0[/bold green][/bold cyan]").strip()

    username = Prompt.ask("[bold cyan]Seu @usuário (apenas identificador local)[/bold cyan]", default="minha_conta").strip()

    with console.status("[bold cyan]Salvando sessão e testando conexão com o X...[/bold cyan]", spinner="dots"):
        try:
            asyncio.run(add_session(auth_token=auth_token, ct0=ct0, raw_cookies=raw_cookies, username=username))
            status = asyncio.run(check_auth_status())
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao configurar sessão:[/bold red] {e}")
            raise typer.Exit(code=1)

    if status.get("authenticated"):
        console.print(f"\n[bold green]✅ Sucesso![/bold green] Sessão validada e pronta para baixar threads.")
    else:
        console.print(f"\n[bold yellow]⚠️ Cookies salvos, mas aviso retornado:[/bold yellow] {status.get('message')}")
        console.print("[dim]Você já pode tentar baixar uma thread com: xthread <url>[/dim]")


@app.command(name="status", help="Verifica a validade da sessão atual e conexões.")
def status():
    """Check session and API connectivity."""
    with console.status("[bold cyan]Verificando credenciais e conexão com o X...[/bold cyan]", spinner="dots"):
        res = asyncio.run(check_auth_status())

    table = Table(title="Status de Conexão do xthread", border_style="cyan")
    table.add_column("Propriedade", style="bold cyan")
    table.add_column("Valor")

    table.add_row("Contas configuradas", str(res["accounts_count"]))
    table.add_row("Contas ativas", str(res.get("active_count", 0)))
    table.add_row(
        "Status da Sessão",
        "[bold green]✓ Autenticado & Ativo[/bold green]" if res["authenticated"] else "[bold red]✗ Inativo ou Não Autenticado[/bold red]",
    )
    table.add_row("Detalhes", res["message"])

    console.print()
    console.print(table)
    console.print()


@app.command(name="logout", help="Remove os cookies e sessões salvas.")
def logout():
    """Clear all saved sessions."""
    if typer.confirm("Tem certeza que deseja desconectar e apagar as sessões salvas?"):
        success = asyncio.run(clear_all_sessions())
        if success:
            console.print("[bold green]✓ Sessões removidas com sucesso.[/bold green]")
        else:
            console.print("[bold red]❌ Erro ao remover banco de dados de sessões.[/bold red]")


@app.command(name="version", help="Exibe a versão do programa.")
def version():
    """Print version."""
    console.print(f"[bold cyan]{APP_NAME}[/bold cyan] versão [bold green]{APP_VERSION}[/bold green]")


def main():
    """Entry point with smart routing for `xthread <url>`."""
    commands = {"status", "auth", "download", "list", "ls", "open", "serve", "logout", "version", "--help", "-h", "--install-completion", "--show-completion"}
    args = sys.argv[1:]

    # If first argument is provided and is not a subcommand or option flag, auto-route to 'download'
    if args and not args[0].startswith("-") and args[0] not in commands:
        sys.argv.insert(1, "download")
    elif not args:
        render_banner()
        # Add --help to display help menu nicely
        sys.argv.append("--help")

    app()


if __name__ == "__main__":
    main()

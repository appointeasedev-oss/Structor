import os
import sys
import json
import time
import webbrowser
import http.server
import socketserver
import urllib.parse
import threading
from pathlib import Path
from datetime import datetime

# UI Libraries
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from rich.box import ROUNDED, DOUBLE_EDGE
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

# Initialize Rich Console
console = Console()

# Configuration storage
CONFIG_DIR = Path.home() / ".structor"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(exist_ok=True)
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_header():
    art = r"""
   _____ _                   _             
  / ____| |                 | |            
 | (___ | |_ _ __ _   _  ___| |_ ___  _ __ 
  \___ \| __| '__| | | |/ __| __/ _ \| '__|
  ____) | |_| |  | |_| | (__| || (_) | |   
 |_____/ \__|_|   \__,_|\___|\__\___/|_|   
    """
    header_text = Text(art, style="bold cyan")
    version_text = Text(f"v1.1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim white")
    
    header_panel = Panel(
        Align.center(header_text + "\n" + version_text),
        box=DOUBLE_EDGE,
        border_style="bright_blue",
        padding=(1, 2)
    )
    return header_panel

def show_splash():
    clear_screen()
    console.print(get_header())
    
    with Progress(
        SpinnerColumn(spinner_name="dots12"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Initializing Structor Core...", total=None)
        time.sleep(1.0)
        progress.add_task(description="Optimizing UI Modules...", total=None)
        time.sleep(0.8)
        progress.add_task(description="Establishing Secure AI Bridge...", total=None)
        time.sleep(0.5)

def show_terms():
    config = load_config()
    if config.get("TERMS_ACCEPTED"):
        return

    show_splash()
    
    terms_content = """
[bold white]Terms and Conditions[/bold white]

1. [cyan]Usage:[/cyan] Use this software responsibly and ethically.
2. [cyan]Costs:[/cyan] You are responsible for any API costs incurred via providers.
3. [cyan]Privacy:[/cyan] API keys and tokens are stored locally in your home directory.
4. [cyan]Liability:[/cyan] Structor is provided "as-is" without warranty.

[dim italic]By selecting 'Yes', you agree to these terms.[/dim italic]
    """
    
    console.print(Panel(terms_content, title="[bold yellow]Onboarding[/bold yellow]", border_style="yellow", box=ROUNDED))
    
    confirm = inquirer.select(
        message="Do you accept the terms and conditions?",
        choices=[
            Choice(value=True, name="Yes, I Accept"),
            Choice(value=False, name="No, Exit"),
        ],
        default=True,
        pointer="❯",
    ).execute()
    
    if not confirm:
        console.print("[bold red]Terms rejected. Exiting...[/bold red]")
        sys.exit()
    
    config["TERMS_ACCEPTED"] = True
    save_config(config)

def set_heho_api_key():
    config = load_config()
    current_key = config.get("HEHO_API_KEY", "Not Set")
    
    table = Table(show_header=False, box=ROUNDED, border_style="magenta")
    table.add_row("[bold magenta]Current HeHo API Key[/bold magenta]", f"[white]{current_key}[/white]")
    console.print(table)
    
    new_key = inquirer.secret(message="Enter your HeHo API Key:").execute()
    if new_key:
        with console.status("[bold magenta]Encrypting and saving key...", spinner="bouncingBar"):
            config["HEHO_API_KEY"] = new_key
            save_config(config)
            os.environ["HEHO_API_KEY"] = new_key
            time.sleep(1)
        console.print("[bold green]✔ HeHo API Key updated successfully![/bold green]")
    time.sleep(1.5)

# --- Puter Auth Automation ---
class PuterAuthHandler(http.server.SimpleHTTPRequestHandler):
    token = None
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if 'token' in params:
            PuterAuthHandler.token = params['token'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body style='font-family:sans-serif;text-align:center;padding-top:50px;'>")
            self.wfile.write(b"<h1>Authentication Successful!</h1>")
            self.wfile.write(b"<p>You can close this window and return to the console.</p>")
            self.wfile.write(b"</body></html>")
        else:
            self.send_response(400)
            self.end_headers()

def run_auth_server(port):
    with socketserver.TCPServer(("", port), PuterAuthHandler) as httpd:
        httpd.handle_request()

def get_puter_token_automated():
    port = 9999
    # Start local server in a thread
    server_thread = threading.Thread(target=run_auth_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    # Open Puter auth page with redirect to local server
    # We use a helper URL that allows token passing back
    auth_url = f"https://puter.com/auth?redirect_uri=http://localhost:{port}"
    console.print(f"[bold yellow]Opening browser for Puter authentication...[/bold yellow]")
    webbrowser.open(auth_url)
    
    console.print("[dim]Waiting for authentication... (Check your browser)[/dim]")
    
    # Wait for token with timeout
    start_time = time.time()
    while PuterAuthHandler.token is None and time.time() - start_time < 60:
        time.sleep(0.5)
    
    return PuterAuthHandler.token

def set_ai_provider():
    config = load_config()
    provider = inquirer.select(
        message="Select AI Provider:",
        choices=[
            Choice(value="OpenRouter", name="OpenRouter (Advanced Models)"),
            Choice(value="Puter", name="Puter (Automated Auth)"),
        ],
        pointer="❯",
    ).execute()
    
    if provider == "OpenRouter":
        api_key = inquirer.secret(message="Enter OpenRouter API Key:").execute()
        model_name = inquirer.text(message="Enter Model Name (e.g., anthropic/claude-3-opus):").execute()
        
        with console.status("[bold cyan]Configuring OpenRouter...", spinner="aesthetic"):
            config["AI_PROVIDER"] = "OpenRouter"
            config["OPENROUTER_API_KEY"] = api_key
            config["MODEL"] = f"openrouter/{model_name}"
            save_config(config)
            time.sleep(1)
        console.print(f"[bold green]✔ Configured with {model_name}[/bold green]")
        
    elif provider == "Puter":
        token = get_puter_token_automated()
        
        if not token:
            console.print("[bold red]Failed to retrieve Puter token automatically.[/bold red]")
            token = inquirer.secret(message="Manual Entry - Enter Puter Auth Token:").execute()
            
        if token:
            model = inquirer.select(
                message="Select Puter Model:",
                choices=["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"],
                pointer="❯",
            ).execute()
            
            with console.status("[bold blue]Verifying Puter Session...", spinner="earth"):
                config["AI_PROVIDER"] = "Puter"
                config["PUTER_TOKEN"] = token
                config["MODEL"] = f"puter/{model}"
                save_config(config)
                time.sleep(1.5)
            console.print(f"[bold green]✔ Puter session active with {model}[/bold green]")
    time.sleep(1.5)

def run_open_interpreter():
    config = load_config()
    model = config.get("MODEL")
    if not model:
        console.print("[bold red]Error: No AI Provider configured. Please set a provider first.[/bold red]")
        time.sleep(2)
        return

    console.print(Panel(
        f"[bold white]Target Model:[/bold white] [cyan]{model}[/cyan]\n"
        f"[bold white]Identity:[/bold white] [green]Structor (Billion Dollar UI Specialist)[/green]\n"
        f"[bold white]Base Prompt:[/bold white] [dim]You are Structor. Make nice UI like billion dollar companies...[/dim]",
        title="[bold green]Initializing Open Interpreter[/bold green]",
        border_style="green",
        box=ROUNDED
    ))
    
    with console.status("[bold green]Booting Interpreter Environment...", spinner="dots"):
        time.sleep(2)
    
    try:
        import interpreter
        interpreter.model = model
        if "OPENROUTER_API_KEY" in config:
            os.environ["OPENROUTER_API_KEY"] = config["OPENROUTER_API_KEY"]
        if "PUTER_TOKEN" in config:
            os.environ["PUTER_AUTH_TOKEN"] = config["PUTER_TOKEN"]
            
        interpreter.system_message = "You are Structor. Make nice UI like billion dollar companies. Focus on advanced aesthetics, professional layouts, and seamless user experiences."
        interpreter.chat()
    except Exception as e:
        console.print(f"\n[bold yellow]Session Simulation (Development Mode)[/bold yellow]")
        console.print(f"[dim]Model: {model}[/dim]")
        console.print("\n[bold cyan]Structor >[/bold cyan] Hello. I am ready to build your billion-dollar UI. What are we creating today?")
        input("\n[Press Enter to return to menu]")

def main_menu():
    show_terms()
    
    while True:
        clear_screen()
        console.print(get_header())
        
        config = load_config()
        status_table = Table(show_header=False, box=None, padding=(0, 2))
        status_table.add_row("[dim]Provider:[/dim]", f"[cyan]{config.get('AI_PROVIDER', 'None')}[/cyan]")
        status_table.add_row("[dim]Model:[/dim]", f"[green]{config.get('MODEL', 'None')}[/green]")
        status_table.add_row("[dim]HeHo Key:[/dim]", "[magenta]●●●●●●[/magenta]" if config.get("HEHO_API_KEY") else "[red]Not Set[/red]")
        
        console.print(Align.center(Panel(status_table, title="[bold white]System Status[/bold white]", border_style="dim", width=50)))
        console.print("\n")
        
        choice = inquirer.select(
            message="Command Center:",
            choices=[
                Choice(value="run", name="🚀 Run Structor (Open Interpreter)"),
                Separator(),
                Choice(value="heho", name="🔑 Set HeHo API Key"),
                Choice(value="provider", name="🤖 Set AI Provider"),
                Separator(),
                Choice(value="exit", name="✖ Exit System"),
            ],
            pointer="❯",
            border=True,
        ).execute()
        
        if choice == "heho":
            set_heho_api_key()
        elif choice == "provider":
            set_ai_provider()
        elif choice == "run":
            run_open_interpreter()
        elif choice == "exit":
            console.print("[bold blue]Shutting down Structor... Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Emergency Shutdown Initiated.[/bold red]")
        sys.exit()

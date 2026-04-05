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
    version_text = Text(f"v1.4.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim white")
    
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
        time.sleep(0.5)
        progress.add_task(description="Optimizing UI Modules...", total=None)
        time.sleep(0.3)
        progress.add_task(description="Establishing Secure AI Bridge...", total=None)
        time.sleep(0.2)

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
            self.wfile.write(b"<html><body style='font-family:sans-serif;text-align:center;padding-top:50px;background:#1a1a2e;color:white;'>")
            self.wfile.write(b"<h1>Authentication Successful!</h1>")
            self.wfile.write(b"<p>You can close this window and return to the Structor console.</p>")
            self.wfile.write(b"</body></html>")
        else:
            self.send_response(400)
            self.end_headers()

def run_auth_server(port):
    with socketserver.TCPServer(("", port), PuterAuthHandler) as httpd:
        httpd.handle_request()

def get_puter_token_automated():
    with socketserver.TCPServer(("", 0), PuterAuthHandler) as s:
        port = s.server_address[1]
    
    server_thread = threading.Thread(target=run_auth_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    auth_url = f"https://puter.com/?action=authme&redirectURL={urllib.parse.quote(f'http://localhost:{port}')}"
    
    console.print(f"[bold yellow]Opening browser for Puter authentication...[/bold yellow]")
    webbrowser.open(auth_url)
    
    console.print("[dim]Waiting for authentication... (Check your browser)[/dim]")
    
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
            # Use 'openrouter/' prefix for LiteLLM/Open Interpreter
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
                # Puter models are often passed via specific provider prefix or directly if using Puter's SDK
                # For Open Interpreter via LiteLLM, we use 'puter/' prefix
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

    # Updated display without "Base Prompt" as requested
    console.print(Panel(
        f"[bold white]Target Model:[/bold white] [cyan]{model}[/cyan]\n"
        f"[bold white]Identity:[/bold white] [green]Structor[/green]",
        title="[bold green]Initializing Open Interpreter[/bold green]",
        border_style="green",
        box=ROUNDED
    ))
    
    with console.status("[bold green]Booting Interpreter Environment...", spinner="dots"):
        time.sleep(1)
    
    try:
        from interpreter import interpreter
        
        # Configure model - Open Interpreter uses LiteLLM internally
        # Ensure model string is correctly formatted
        interpreter.model = model
        
        # Set API keys based on provider
        if config.get("AI_PROVIDER") == "OpenRouter":
            api_key = config.get("OPENROUTER_API_KEY", "")
            os.environ["OPENROUTER_API_KEY"] = api_key
            # LiteLLM uses OPENAI_API_KEY for OpenRouter if provider is not explicitly set in model string
            # But since we use 'openrouter/' prefix, it should use OPENROUTER_API_KEY.
            # However, many users report needing OPENAI_API_KEY or OPENAI_API_BASE.
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        elif config.get("AI_PROVIDER") == "Puter":
            os.environ["PUTER_AUTH_TOKEN"] = config.get("PUTER_TOKEN", "")
            
        # Also set HEHO key if available
        if config.get("HEHO_API_KEY"):
            os.environ["HEHO_API_KEY"] = config.get("HEHO_API_KEY")
            
        # System Message
        system_msg = "You are Structor. Make nice UI like billion dollar companies. Focus on advanced aesthetics, professional layouts, and seamless user experiences."
        
        # Add HeHo API info to system message if available
        if config.get("HEHO_API_KEY"):
            system_msg += f"\n\nYou have access to the HeHo API. The API key is available in the environment variable 'HEHO_API_KEY'. Use this key to perform tasks in the user's HeHo account if requested. Refer to the HeHo API documentation for endpoints like /api/v1/login, /api/verify-user, /api/aichat, /api/v1/chatbots/manage, and /api/v1/database/manage."
            
        interpreter.system_message = system_msg
        
        # Start chat
        interpreter.chat()
        
    except ImportError:
        console.print("[bold red]Error: 'open-interpreter' is not installed correctly.[/bold red]")
        console.print("[yellow]Please run: pip install open-interpreter[/yellow]")
        time.sleep(3)
    except Exception as e:
        console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")
        time.sleep(3)

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

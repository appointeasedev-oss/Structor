import os
import sys
import json
import time
import webbrowser
import requests
from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

# Configuration storage
CONFIG_DIR = Path.home() / ".structor"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(exist_ok=True)
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_art():
    art = r"""
  ____  _                   _             
 / ___|| |_ _ __ _   _  ___| |_ ___  _ __ 
 \___ \| __| '__| | | |/ __| __/ _ \| '__|
  ___) | |_| |  | |_| | (__| || (_) | |   
 |____/ \__|_|   \__,_|\___|\__\___/|_|   
                                           
    """
    print(art)

def show_terms():
    show_art()
    print("\n--- TERMS AND CONDITIONS ---")
    print("1. Use this software responsibly.")
    print("2. AI providers may charge for API usage.")
    print("3. Your API keys are stored locally.")
    print("----------------------------\n")
    
    confirm = inquirer.select(
        message="Do you accept the terms and conditions?",
        choices=[
            Choice(value=True, name="Yes"),
            Choice(value=False, name="No"),
        ],
        default=True,
    ).execute()
    
    if not confirm:
        print("You must accept the terms to use Structor. Exiting...")
        sys.exit()

def set_heho_api_key():
    config = load_config()
    current_key = config.get("HEHO_API_KEY", "Not Set")
    print(f"\nCurrent HeHo API Key: {current_key}")
    
    new_key = inquirer.text(message="Enter your HeHo API Key:").execute()
    if new_key:
        config["HEHO_API_KEY"] = new_key
        save_config(config)
        os.environ["HEHO_API_KEY"] = new_key
        print("HeHo API Key set successfully!")
    time.sleep(1)

def set_ai_provider():
    config = load_config()
    provider = inquirer.select(
        message="Select AI Provider:",
        choices=["OpenRouter", "Puter"],
    ).execute()
    
    if provider == "OpenRouter":
        api_key = inquirer.text(message="Enter OpenRouter API Key:").execute()
        model_name = inquirer.text(message="Enter Model Name (e.g., anthropic/claude-3-opus):").execute()
        config["AI_PROVIDER"] = "OpenRouter"
        config["OPENROUTER_API_KEY"] = api_key
        config["MODEL"] = f"openrouter/{model_name}"
        save_config(config)
        print(f"OpenRouter configured with model: {model_name}")
        
    elif provider == "Puter":
        print("Opening Puter Auth in browser...")
        # In a real headless app, we'd handle OAuth. 
        # For this mock, we'll simulate the flow.
        webbrowser.open("https://puter.com/auth")
        token = inquirer.text(message="Enter Puter Auth Token:").execute()
        # Mocking model selection for Puter
        model = inquirer.select(
            message="Select Puter Model:",
            choices=["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"],
        ).execute()
        config["AI_PROVIDER"] = "Puter"
        config["PUTER_TOKEN"] = token
        config["MODEL"] = f"puter/{model}"
        save_config(config)
        print(f"Puter configured with model: {model}")
    time.sleep(1)

def run_open_interpreter():
    config = load_config()
    model = config.get("MODEL")
    if not model:
        print("Error: AI Provider not configured. Please run 'Set AI Provider' first.")
        time.sleep(2)
        return

    print(f"\nStarting Open Interpreter with model: {model}")
    print("Base Prompt: You are Structor. Make nice UI like billion dollar companies.")
    
    # In a real implementation, we would call open-interpreter here.
    # For now, we simulate the environment.
    try:
        import interpreter
        interpreter.model = model
        if "OPENROUTER_API_KEY" in config:
            os.environ["OPENROUTER_API_KEY"] = config["OPENROUTER_API_KEY"]
        interpreter.chat("You are Structor. Make nice UI like billion dollar companies. How can I help you today?")
    except ImportError:
        print("\n[MOCK] Open Interpreter session started.")
        print(f"Model: {model}")
        print("Prompt: You are Structor...")
        input("\nPress Enter to return to menu...")

def main_menu():
    show_terms()
    first_run = True
    
    while True:
        clear_screen()
        if first_run:
            show_art()
            first_run = False
        
        choice = inquirer.select(
            message="Select a command:",
            choices=[
                Choice(value="heho", name="Set HeHo API Key"),
                Choice(value="provider", name="Set AI Provider"),
                Choice(value="run", name="Run Structor (Open Interpreter)"),
                Choice(value="exit", name="Exit"),
            ],
            border=True,
        ).execute()
        
        if choice == "heho":
            set_heho_api_key()
        elif choice == "provider":
            set_ai_provider()
        elif choice == "run":
            run_open_interpreter()
        elif choice == "exit":
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

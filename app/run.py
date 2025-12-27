import subprocess
import requests
import webbrowser
import time
import os
from typing import Optional, Dict, Any
from rich.theme import Theme
from rich.console import Console

def handle_error(error: Exception, context: str = "") -> None:    
    error_msg = f"Erreur dans {context}: {str(error)}"
    display.print(f"[bright_red]❌ {error_msg}")

def display_prompt(ai=None, mmproj=None) -> None:    
    if ai:
        display.print("IA sélectionnée")
        display.print(f"[bright_yellow on bright_magenta] * {ai}")
    if mmproj:
        display.print("Multi modal projection sélectionné")
        display.print(f"[bright_yellow on bright_magenta] * {mmproj}")

def get_user_selection(prompt: str, options: list[str]) -> int:    
    display.print(prompt)
    while True:        
        for i, option in enumerate(options, 1):
            display.print(f"{i}. [bright_yellow]{option}")
        try:
            choice = display.input("Entrez le numéro de votre choix: ")
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                os.system("cls")
                return idx
            else:
                display.print(f"Veuillez entrer un nombre entre 1 et {len(options)}")
        except ValueError:
            display.print("Veuillez entrer un nombre valide")

def launch_llama_server(server: str, url: str, port: str, modelgguf: str, modelmmproj: str) -> Optional[subprocess.Popen]:    
    display.print("Lancement de llama-serveur...")
    try:
        process = subprocess.Popen([server, "--host", "0.0.0.0", "--port", port, "--model", modelgguf, "--mmproj", modelmmproj, "--ctx_size", "16384", "--threads", "8", "--batch_size", "4", "-t", "0.125"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        max_retries = 30
        retry_delay = 1
        for _ in range(max_retries):
            time.sleep(retry_delay)
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                webbrowser.open(url)
                display.print("[bright_yellow on bright_magenta] * Serveur lancé")
                return process
            except requests.exceptions.RequestException as e:
                continue
        handle_error(e)
        process.terminate()
        process.wait()
        return None

    except Exception as e:
        process.terminate()
        process.wait()
        handle_error(e)
        return None

if __name__ == "__main__":
    SERVER_PATH = "llama\\llama-server.exe"
    PORT = "8080"    
    URL = f"http://127.0.0.1:{PORT}"
    MODEL_BASE = f"models\\mistralai"

    display = Console(
        style="bright_cyan",
        force_terminal=True,
        color_system="truecolor",
        legacy_windows=True
    )
    files = [file for file in os.listdir(MODEL_BASE) if file.endswith('.gguf')]
    if not files:
        display.print("Aucun fichier trouvé. Quiting.")
    else:
        # Sélection des fichiers
        gguf_idx = get_user_selection("Sélectionnez une IA:", files)
        model_gguf = files[gguf_idx]
        display_prompt(files[gguf_idx])
        files_copy = files[:]
        files_copy.remove(model_gguf)
        if gguf_idx == len(files) - 1:
            gguf_idx = len(files_copy) - 1
        mmproj_idx = get_user_selection("Sélectionnez un multi modal projection (mmproj):", files_copy)
        model_mmproj = files_copy[mmproj_idx]
        display_prompt(files[gguf_idx], files_copy[mmproj_idx])
        MODEL_GGUF = f'{MODEL_BASE}\\{model_gguf}'
        MODEL_MMPROJ = f'{MODEL_BASE}\\{model_mmproj}'
        # Lancement du serveur
        process = launch_llama_server(SERVER_PATH, URL, PORT, MODEL_GGUF, MODEL_MMPROJ)
        if process:
            display.print(f"[bright_cyan]Serveur en cours d'exécution (PID:{process.pid})")
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()

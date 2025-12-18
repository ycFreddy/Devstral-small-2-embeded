import subprocess
import requests
import webbrowser
import time
import os
from typing import Optional, Dict, Any

def handle_error(error: Exception, context: str = "") -> None:
    """Gère les erreurs de manière centralisée avec un message contextualisé."""
    error_msg = f"Erreur dans {context}: {str(error)}"
    print(f"❌ {error_msg}")

def load_config_from_file(file_path: str) -> Dict[str, str]:
    """Charge la configuration depuis un fichier."""
    print(" Chargement de la configuration..")
    config = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Ignorer les lignes vides ou les commentaires
                if not line or line.startswith('#'):
                    continue
                # Diviser en clé et valeur
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')  # Enlever les guillemets
                    config[key] = value
        print(" * Configuration chargée")
        return config

    except FileNotFoundError as e:
        handle_error(e, "le chargement de la configuration")
        return {}
    except Exception as e:
        handle_error(e, "le chargement de la configuration")
        return {}

def check_files_exist(model_gguf_path: str, model_mmproj_path: str) -> Dict[str, bool]:
    """Vérifie l'existence des fichiers de modèle."""
    print(" Vérification des modèles..")
    results = {
        'GGUF_model_exists': os.path.exists(model_gguf_path),
        'MMPROJ_model_exists': os.path.exists(model_mmproj_path),
        'all_exist': os.path.exists(model_gguf_path) and os.path.exists(model_mmproj_path)
    }

    if not results['GGUF_model_exists']:
        handle_error(FileNotFoundError(f"Modèle GGUF introuvable: {model_gguf_path}"), "la vérification des modèles")
    else:
        print(" * Modèle gguf -> OK")
    if not results['MMPROJ_model_exists']:
        handle_error(FileNotFoundError(f"Modèle MMPROJ introuvable: {model_mmproj_path}"), "la vérification des modèles")        
    else:
        print(" * Modèle mmproj -> OK")
    
    return results

def launch_llama_server(server: str, url: str, modelgguf: str, modelmmproj: str) -> Optional[subprocess.Popen]:
    """Lance le serveur Llama avec gestion des erreurs."""
    print(" Lancement de llama-serveur..")

    try:
        # Lancer le serveur dans un processus séparé
        process = subprocess.Popen(
            [server, "--model", modelgguf, "--mmproj", modelmmproj, "--ctx_size", "16384", "--batch_size", "1", "-t", "0.125"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Attendre que le serveur soit prêt (jusqu'à 30 secondes max)
        max_retries = 30
        retry_delay = 1
        for _ in range(max_retries):
            time.sleep(retry_delay)
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                webbrowser.open(url)
                print(" * Serveur lancé")
                return process

            except requests.exceptions.RequestException as e:
                continue

        # Si on arrive ici, le serveur n'a pas répondu à temps
        handle_error(Exception("Serveur non répondant après 30 secondes"), "le démarrage du serveur")
        process.terminate()
        stdout, stderr = process.communicate()
        print("Sortie standard :", stdout.decode() if stdout else "Aucune sortie")
        print("Erreurs :", stderr.decode() if stderr else "Aucune erreur")
        return None

    except Exception as e:
        handle_error(e, "le lancement du serveur")
        return None

def main():
    SERVER = "llama\\llama-server.exe"
    URL = "http://localhost:8080"
    MODEL_BASE = f"models\\mistralai"

    # Chargement de la configuration
    config = load_config_from_file("config.txt")
    if not config:
        return

    MODEL_GGUF = f"{MODEL_BASE}\\{config.get('MODEL_GGUF')}"
    MODEL_MMPROJ = f"{MODEL_BASE}\\{config.get('MODEL_MMPROJ')}"

    # Vérification des modèles
    results = check_files_exist(MODEL_GGUF, MODEL_MMPROJ)
    if not results['all_exist']:
        return

    # Lancement du serveur
    '''process = launch_llama_server(SERVER, URL, MODEL_GGUF, MODEL_MMPROJ)
    if process:
        print("Serveur en cours d'exécution (PID:", process.pid, ")")
        try:
            process.wait()  # Attendre la fin du processus
        except KeyboardInterrupt:
            print("Arrêt du serveur...")
            process.terminate()'''

if __name__ == "__main__":
    main()

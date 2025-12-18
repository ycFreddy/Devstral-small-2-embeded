import subprocess
import requests
import webbrowser
import time


def launch_llama_server(server, url, modelgguf, modelmmproj):
    print(" Lancement de llama-serveur..")

    # Lancer le serveur dans un processus séparé
    process = subprocess.Popen(
        [server, "--model", modelgguf, "--mmproj", modelmmproj, "--ctx_size", "32768", "--batch_size", "8", "-t", "1.25"],
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
            return process  # Retourne le processus pour une gestion ultérieure
        except requests.exceptions.RequestException:
            continue

    # Si on arrive ici, le serveur n'a pas répondu à temps
    process.terminate()
    stdout, stderr = process.communicate()
    print("Erreur : Le serveur n'a pas démarré correctement.")
    print("Sortie standard :", stdout.decode() if stdout else "Aucune sortie")
    print("Erreurs :", stderr.decode() if stderr else "Aucune erreur")
    return None

def load_config_from_file(file_path):
    print(" Chargement des modèles..")
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
            print(" * Modèles chargés")

    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier config non trouvé: {file_path}")

    return config

if __name__ == "__main__":
    SERVER = "llama\\llama-server.exe" 
    URL = "http://localhost:8080"
    try:
        config = load_config_from_file("config.txt")
        MODEL_GGUF = f"models\\mistralai\\{config.get('MODEL_GGUF')}"
        MODEL_MMPROJ = f"models\\mistralai\\{config.get('MODEL_MMPROJ')}"
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
    
    launch_llama_server(SERVER, URL, MODEL_GGUF, MODEL_MMPROJ)

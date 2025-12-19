@echo off
chcp 65001 >nul
echo ---
.\python-3.12.9-amd64\python.exe app\run.py
if %errorlevel% neq 0 (
    echo Erreur lors de l'exécution
)
echo ---
echo Fermer la fenêtre pour quitter
pause >nul
import sys
import os

# Rediriger la sortie standard (print) vers le fichier de log d'Apache
sys.stdout = sys.stderr

# Chemin vers l'environnement virtuel
venv_path = '/var/www/melange_magique/mistral_env'

# Ajouter le dossier des paquets du venv à sys.path
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.9', 'site-packages'))

sys.path.insert(0, '/var/www/melange_magique')

# Définir les variables d'environnement pour activer l'environnement virtuel
os.environ['VIRTUAL_ENV'] = venv_path
os.environ['PATH'] = os.path.join(venv_path, 'bin') + ':' + os.environ['PATH']

from app import app as application

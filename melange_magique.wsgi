import sys
import os

# Chemin vers le fichier de log de l'application
log_path = '/var/www/melange_magique/melange_magique_app.log'

# Rediriger stdout et stderr vers un fichier de log
sys.stdout = open(log_path, 'a')  # Mode append pour conserver l'historique
sys.stderr = sys.stdout  # Les erreurs vont aussi dans ce fichier

# Chemin vers l'environnement virtuel
venv_path = '/var/www/melange_magique/mistral_env'

# Ajouter le dossier des paquets du venv à sys.path
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.9', 'site-packages'))

sys.path.insert(0, '/var/www/melange_magique')

# Définir les variables d'environnement pour activer l'environnement virtuel
os.environ['VIRTUAL_ENV'] = venv_path
os.environ['PATH'] = os.path.join(venv_path, 'bin') + ':' + os.environ['PATH']

from app import app as application

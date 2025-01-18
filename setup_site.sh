#!/bin/bash

# Vérification si le script est exécuté en tant que root
if [ "$(id -u)" -ne 0 ]; then
    echo "Veuillez exécuter ce script en tant que root."
    exit 1
fi

# Variables
USERNAME="behhuser"
USER_PASSWORD="BEHH!?9user!?7"
PROJECT_DIR="/var/www/melange_magique"
REPO_URL="https://Lu2ovic:$GIT_TOKEN@github.com/SAE501-Team/SAE501-melange-magique.git"
APACHE_SSL_DIR="/etc/apache2/ssl"
SSL_KEY="$APACHE_SSL_DIR/melange_magique.key"
SSL_CERT="$APACHE_SSL_DIR/melange_magique.crt"
GIT_TOKEN_FILE="/root/.env"

# Création de l'utilisateur
echo "Création de l'utilisateur $USERNAME..."
adduser --disabled-password --gecos "" $USERNAME
echo "$USERNAME:$USER_PASSWORD" | chpasswd

# Mise à jour et installation des paquets requis
echo "Mise à jour des paquets..."
apt update && apt upgrade -y

echo "Installation des dépendances..."
apt install -y apache2 libapache2-mod-wsgi-py3 git python3-venv openssl

# Désactiver l'accès SSH pour root
echo "Désactivation de l'accès SSH pour root..."
SSHD_CONFIG="/etc/ssh/sshd_config"
cp $SSHD_CONFIG $SSHD_CONFIG.bak
sed -i 's/^#*PermitRootLogin yes/PermitRootLogin no/' $SSHD_CONFIG
systemctl restart sshd

# Configuration du projet
echo "Clonage du dépôt Git..."
mkdir -p $PROJECT_DIR
cd /var/www
git clone $REPO_URL melange_magique
cd $PROJECT_DIR
git config --global --add safe.directory $PROJECT_DIR
git config --global user.name "Lu2ovic"
git config --global user.email "ludovic.hauptmann1@gmail.com"

# Configurer Python
echo "Configuration de l'environnement Python..."
python3 -m venv mistral_env
source mistral_env/bin/activate
pip install -r requirements.txt
deactivate

# Configuration Apache
echo "Configuration d'Apache..."
cat <<EOL > /etc/apache2/sites-available/melange_magique.conf
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot $PROJECT_DIR
    Redirect permanent / https://87.106.123.82/
</VirtualHost>
EOL

a2ensite melange_magique.conf
systemctl restart apache2

# Configuration SSL
echo "Configuration SSL..."
mkdir -p $APACHE_SSL_DIR
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $SSL_KEY \
    -out $SSL_CERT \
    -subj "/C=FR/ST=Ile-de-France/L=Paris/O=MonSite/OU=IT/CN=87.106.123.82"

cat <<EOL > /etc/apache2/sites-available/melange_magique_ssl.conf
<VirtualHost *:443>
    ServerName 87.106.123.82

    DocumentRoot $PROJECT_DIR

    SSLEngine on
    SSLCertificateFile $SSL_CERT
    SSLCertificateKeyFile $SSL_KEY

    WSGIDaemonProcess melange_magique python-home=$PROJECT_DIR/mistral_env python-path=$PROJECT_DIR
    WSGIProcessGroup melange_magique
    WSGIScriptAlias / $PROJECT_DIR/melange_magique.wsgi

    <Directory $PROJECT_DIR>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOL

a2enmod ssl
a2ensite melange_magique_ssl.conf
systemctl restart apache2

# Automatisation des mises à jour avec Cron
echo "Configuration des mises à jour automatiques..."
cat <<EOL > $PROJECT_DIR/update_git.sh
#!/bin/bash
source $GIT_TOKEN_FILE
cd $PROJECT_DIR
git add donnee_cereales_test.py
git commit -m "Auto-update donnee_cereales_test.py"
git push origin main
EOL

chmod +x $PROJECT_DIR/update_git.sh
(crontab -l 2>/dev/null; echo "0 * * * * $PROJECT_DIR/update_git.sh >> /var/log/update_git.log 2>&1") | crontab -

echo "Configuration terminée. Le site est maintenant opérationnel."

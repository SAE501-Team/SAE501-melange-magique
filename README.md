À faire pour mettre en place le site sur un vps réinitialisé

#Placer le tocken git
echo "GIT_TOKEN=ghp_yourtokenhere" > /root/.env

cd /root

nano setup_site.sh 
-> copier le contenu de se fichier du github vers celui du vps

#rendre fichier exécutable :
chmod +x setup_site.sh 

#exécuter le scripte : 
./setup_site.sh

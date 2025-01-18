#!/bin/bash

# Dossier du projet
PROJECT_DIR="/var/www/melange_magique"
FILE_TO_UPDATE="donnee_cereales_test.py"
BRANCH="main"  # Remplacez par le nom de votre branche si ce n'est pas "main"

# Aller dans le dossier du projet
cd $PROJECT_DIR || { echo "Erreur: impossible d'accéder au dossier $PROJECT_DIR"; exit 1; }

# Ajouter les modifications
git add $FILE_TO_UPDATE

# Vérifier s'il y a des modifications à committer
if git diff-index --quiet HEAD --; then
    echo "Aucune modification détectée dans $FILE_TO_UPDATE. Rien à committer."
else
    # Commit des modifications
    git commit -m "Mise à jour automatique de $FILE_TO_UPDATE ($(date))"

    # Pousser les modifications
    git push origin $BRANCH
    echo "Mise à jour poussée sur la branche $BRANCH."
fi

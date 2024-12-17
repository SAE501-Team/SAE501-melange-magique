import random
import string


def generer_reference(categorie, produit_nom):
    # Générer un identifiant aléatoire de 4 caractères (pour rendre chaque référence unique)
    identifiant = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Utiliser les 3 premières lettres de la catégorie et du nom du produit
    ref_categorie = categorie[:3].upper()
    ref_produit = produit_nom[:3].upper()
    
    # Construire la référence unique sous forme de : CAT-PRO-ID
    reference = f"{ref_categorie}-{ref_produit}-{identifiant}"
    
    return reference

# Exemple d'utilisation
categorie = "Céréales"
produit_nom = "Cornflakes"

# Générer une référence pour le produit
reference = generer_reference(categorie, produit_nom)
print(f"Référence générée pour {produit_nom} : {reference}")

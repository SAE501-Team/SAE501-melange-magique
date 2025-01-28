import random
from product_generate_reference import generer_reference
from generate_text import generate_cereal_info
from calcul_prix import calcul_prix
from creat_prompt import creat_prompt
from generate_img import generate_product_images
from creat_prompt_img import creat_prompt_img
from productSend import ajouter_produit
import time
from datetime import datetime, timedelta

formes_disponibles = [8, 7, 11, 9, 12, 13, 14, 15, 10] 
gouts_disponibles = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

# Limites
QUOTA_MINUTE = 15
QUOTA_DAILY = 1000
SAFE_MARGIN = 950  # Pour arrêter avant d'atteindre le maximum (ex. à 950/1000)

# Compteurs
requests_minute = 0
requests_daily = 0
minute_start_time = datetime.now()
day_start_time = datetime.now()

# Fonction pour limiter à 15 requêtes par minute
def wait_for_minute_reset():
    """Attendre jusqu'à ce que le quota par minute soit réinitialisé."""
    global minute_start_time, requests_minute
    now = datetime.now()
    elapsed = (now - minute_start_time).total_seconds()
    if elapsed < 60:
        wait_time = 60 - elapsed
        print(f"Quota minute atteint. Attente de {wait_time:.1f} secondes...")
        time.sleep(wait_time)
    # Réinitialiser les compteurs minute
    minute_start_time = datetime.now()
    requests_minute = 0

# Fonction pour vérifier le quota quotidien
def check_daily_quota():
    """Vérifier si le quota quotidien est atteint."""
    global requests_daily, day_start_time
    if requests_daily >= QUOTA_DAILY - SAFE_MARGIN:
        now = datetime.now()
        next_day = day_start_time + timedelta(days=1)
        time_remaining = (next_day - now).total_seconds()
        hours, remainder = divmod(time_remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Quota quotidien atteint ({requests_daily}/{QUOTA_DAILY})."
              f" Revenez dans {int(hours)}h {int(minutes)}m {int(seconds)}s.")
        exit(0)
        

def generer_caract(formes_disponibles, gouts_disponibles):
    """
    Génère un produit en sélectionnant aléatoirement 1 à 3 formes et 1 à 3 goûts.
    
    :param formes_disponibles: Liste des numéros correspondant aux formes.
    :param gouts_disponibles: Liste des numéros correspondant aux goûts.
    :return: Un dictionnaire {"formes": [...], "gouts": [...]}.
    """
    # Sélectionner de 1 à 2 formes
    formes_choisies = random.sample(formes_disponibles, random.randint(1, min(2, len(formes_disponibles))))
    
    # Sélectionner de 1 à 3 goûts proba 50%, 35%, 15%
    gouts_choisis = random.sample(gouts_disponibles, random.choices([1, 2, 3], weights=[0.5, 0.4, 0.1], k=1)[0])
    
    return {"formes": formes_choisies, "gouts": gouts_choisis}


def generate_product(nom, reference, prix, description, meta_description, meta_title, link_rewrite, categories, attributs, caracteristiques, images):
    """
    Fonction pour générer un produit avec les informations fournies.
    
    Args:
        nom (str): Le nom du produit.
        reference (str): La référence du produit.
        prix (float): Le prix du produit.
        description (str): La description du produit.
        categories (list): Liste des catégories du produit.
        attributs (dict): Dictionnaire des attributs du produit.
        caracteristiques (dict): Dictionnaire des caractéristiques du produit.
    
    Returns:
        dict: Dictionnaire représentant le produit.
    """
    product = {
        "nom": nom,
        "reference": reference,
        "prix": prix,
        "description": description,
        "meta_description": meta_description,
        "meta_title": meta_title,
        "link_rewrite": link_rewrite,
        "id_categories": categories,
        "attributs": attributs,
        "caracteristiques": caracteristiques,
        "images": images
    }
    return product

def generate_products(n):
    """
    Fonction pour générer une liste de n produits.
    
    Args:
        n (int): Le nombre de produits à générer.
    
    Returns:
        str: Message de succès indiquant que tous les produits ont été créés et ajoutés.
    """

    global requests_minute, requests_daily
    produits_ajoutes = 0
    produits_non_envoies = 0  # Compteur pour les produits non envoyés

    for i in range(n):
        try:
            # Vérifier si le quota quotidien est atteint
            check_daily_quota()

            # Limiter à 15 requêtes par minute
            if requests_minute >= QUOTA_MINUTE:
                wait_for_minute_reset()

            # Générer des catégories aléatoires
            categories = [random.choice([11, 12, 13]),2,10]   # Vérifier et changer les ID si nécessaire
            attribut = {"taille": [1, 2, 3]}
            caracteristique = generer_caract(formes_disponibles, gouts_disponibles)
            
            # Générer les informations du produit
            infos_product = generate_cereal_info(creat_prompt(caracteristique, categories))
            name = infos_product["nom_produit"]
            description = infos_product["description"]
            meta_description = infos_product["meta_description"]
            meta_title = infos_product["meta_title"]
            link_rewrite = infos_product["link_rewrite"]
            ref = generer_reference("Cereales", name)
            # Générer les images du produit
            images_gen = generate_product_images(creat_prompt_img(caracteristique, categories, name), ref)

            if len(images_gen) != 2:
                print(f"Produit {name} : Nombre d'images insuffisant, produit non envoyé.")
                produits_non_envoies += 1  # Incrémenter le compteur des produits non envoyés
                continue  # Passer au produit suivant
            
            # Créer l'objet produit
            product = generate_product(
                nom=name,
                reference=ref,
                prix=calcul_prix(caracteristique, categories),  # Prix basé sur les caractéristiques
                description=description,
                meta_description=meta_description,
                meta_title=meta_title,
                link_rewrite=link_rewrite,
                categories=categories,
                attributs=attribut,
                caracteristiques=caracteristique,
                images=images_gen
            )

            # Ajouter le produit et afficher un message
            ajouter_produit(product, "/Volumes/My Passport/melange_magique/product/imgProduit")
            print(f"Produit numéro {i + 1}/{n} ajouté au site BEHH")

            # Incrémenter les compteurs
            produits_ajoutes += 1
            requests_minute += 1
            requests_daily += 1

            time.sleep(2)

        except Exception as e:
            # Afficher un message d'erreur s'il y a un problème
            print(f"Erreur lors de l'ajout du produit numéro {i + 1} : {e}")
            produits_non_envoies += 1

    print(f"{produits_ajoutes} produit(s) ajouté(s) avec succès.")
    if produits_non_envoies > 0:
        print(f"{produits_non_envoies} produit(s) n'ont pas pu être envoyé(s).")
        
    return "Tous les produits ont été créés et ajoutés au site BEHH avec succès ! 🫡 🐐"


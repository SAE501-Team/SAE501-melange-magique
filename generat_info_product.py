formes_cereales = [
    "flocon",
    "boule",
    "anneau",
    "cube",
    "bâtonnet",
    "grain soufflé",
    "pépite",
    "étoile",
    "pétale"
]

gouts_cereales = [
    "chocolat",
    "vanille",
    "miel",
    "fruits rouges",
    "caramel",
    "cannelle",
    "noisette",
    "spéculoos",
    "nature",
    "sucrée"
]

categorie_cereales = [
    "bio",
    "sport",
    "gourmand"
]

import random
from product_generate_reference import generer_reference

def generate_product(nom, reference, prix, description, categories, attributs, caracteristiques):
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
        "meta_description": "",
        "meta_title": "",
        "link_rewrite": "",
        "id_categories": categories,
        "attributs": attributs,
        "caracteristiques": caracteristiques
    }
    return product

def generate_products(n):
    """
    Fonction pour générer une liste de n produits.
    
    Args:
        n (int): Le nombre de produits à générer.
    
    Returns:
        list: Liste de n produits générée.
    """
    products = []
    
    # Liste de base de produits avec des données génériques
    names = ["Céréales Choco Boule", "Céréales Fruits Mix", "Céréales Nature", "Céréales Miel Crunch", "Céréales Avoine"]
    descriptions = [
        "Délicieuses boules au chocolat.",
        "Mélange fruité de céréales.",
        "Céréales simples et saines.",
        "Céréales croquantes au miel.",
        "Céréales à base d'avoine pour un petit-déjeuner sain."
    ]
    categories = [9]
    attributs = [{"taille": 1}, {"taille": 2}]
    caracteristiques = [{"formes": [7, 8], "gouts": [22, 23]}, {"formes": [6, 10], "gouts": [20, 25]}]
    
    # Générer n produits en utilisant des données aléatoires ou répétitives
    for i in range(n):
        name = random.choice(names)
        description = random.choice(descriptions)
        attribut = random.choice(attributs)
        caracteristique = random.choice(caracteristiques)
        
        product = generate_product(
            nom=name,
            reference=generer_reference("Céréales", name),
            prix=round(random.uniform(3.99, 9.99), 2),  # Prix aléatoire entre 3.99 et 9.99
            description=description,
            categories=categories,
            attributs=attribut,
            caracteristiques=caracteristique
        )
        
        products.append(product)

    return products

from donnee_cereales_test import formes_cereales, gouts_cereales, categorie_cereales
from app_generate_text import generate_cereal_info

def app_creat_prompt(caracteristique, categorieone, titre):

    def format_list(items):
        if len(items) > 1:
            return ", ".join(items[:-1]) + " et " + items[-1]
        elif items:
            return items[0]
        return ""

    # Récupérer les noms des formes
    formes = [
        formes_cereales.get(forme_id, {}).get("nom", "")
        for forme_id in caracteristique.get("formes", [])
    ]

    # Récupérer les noms des goûts
    gouts = [
        gouts_cereales.get(gout_id, {}).get("nom", "")
        for gout_id in caracteristique.get("gouts", [])
    ]

    
    # Récupérer les noms des catégories
    categorie = [
        categorie_cereales.get(categorie_id, {}).get("nom", "")
        for categorie_id in [categorieone]
    ]

    # Construire les chaînes formatées
    formes_str = format_list([f for f in formes if f])
    gouts_str = format_list([g for g in gouts if g])
    categorie_str = format_list([c for c in categorie if c])

    return "Génère des informations pour une seul boite de cereal de catégorie "+categorie_str+", de goût "+gouts_str+", en forme de "+formes_str+". Elle a pour nom : '"+titre+"'. Sachant que c'est pour un site de e-commerce qui vend des céréales. Je veux que tu me le génère sous cette forme : ['description','meta_description','meta_title en lien avec le nom du produit','link_rewrite (nom-du-produit)]"


'''code pour test
infos_product = generate_cereal_info(app_creat_prompt({"formes": [9,10], "gouts": [23,24]}, [4], "Test cereales"))
description = infos_product["description"]
meta_description = infos_product["meta_description"]
meta_title = infos_product["meta_title"]
link_rewrite = infos_product["link_rewrite"]
print(infos_product)
print(description)
print(meta_description)
print(meta_title)
print(link_rewrite)'''
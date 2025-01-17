from donnee_cereales import formes_cereales, gouts_cereales, categorie_cereales

def creat_prompt(caracteristique, categories):

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
        for categorie_id in categories
    ]

    # Construire les chaînes formatées
    formes_str = format_list([f for f in formes if f])
    gouts_str = format_list([g for g in gouts if g])
    categorie_str = format_list([c for c in categorie if c])

    return "Génère des informations pour une seul boite de cereal de catégorie "+categorie_str+", de goût "+gouts_str+", en forme de "+formes_str+". Sachant que c'est pour un site de e-commerce qui vend des céréales. Je veux que tu me le génère sous cette forme : ['nom Produit créatif pas trop long','description','meta_description','meta_title en lien avec le nom du produit','link_rewrite (nom-du-produit)]"





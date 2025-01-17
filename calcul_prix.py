from donnee_cereales import formes_cereales, gouts_cereales, categorie_cereales

def calcul_prix(caracteristique, categories, prix_total=0.0):

    # Calculer le prix pour les formes
    for forme_id in caracteristique.get("formes", []):
        prix_total += formes_cereales.get(forme_id, {}).get("prix", 0)

    # Calculer le prix pour les goûts
    for gout_id in caracteristique.get("gouts", []):
        prix_total += gouts_cereales.get(gout_id, {}).get("prix", 0)

    # Calculer le prix pour les catégories
    for categorie_id in categories:
        prix_total += categorie_cereales.get(categorie_id, {}).get("prix", 0)

    return round(prix_total, 2)


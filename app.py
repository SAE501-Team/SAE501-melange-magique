from flask import Flask, request, render_template
import donnee_cereales_test
from app_ia_verif_caract import ia_verif_caract
from fuzzywuzzy import fuzz
from app_caract_send import ajouter_valeur_caracteristique
from app_add_caract_donnee import ajouter_element
from generat_info_product import ajouter_produit, generate_product
from calcul_prix import calcul_prix
from app_creat_prompt import app_creat_prompt
from product_generate_reference import generer_reference
from app_generate_text import generate_cereal_info
from generate_img import generate_product_images
from app_creat_prompt_img import app_creat_prompt_img
from app_secur import APILimiter
import time

app = Flask(__name__)

# Initialiser le limiteur API
api_limiter = APILimiter(max_per_minute=14, max_per_day=998)

def nettoyer_valeur(valeur):
    """
    Nettoie une valeur en supprimant les espaces inutiles et en la mettant en minuscule.
    :param valeur: la valeur à nettoyer
    :return: la valeur nettoyée
    """
    return valeur.strip().lower()

def verifier_si_existe(valeur, type_choix, seuil_similarite=80):
    """
    Vérifie si la valeur donnée correspond à un nom valide dans les dictionnaires de formes ou de goûts.
    Permet une tolérance aux fautes mineures.
    :param valeur: la valeur à vérifier
    :param type_choix: type de choix (soit 'forme', soit 'gout')
    :param seuil_similarite: pourcentage minimal de similarité pour considérer une correspondance
    :return: l'ID correspondant ou None si la valeur n'existe pas
    """
    valeur_nettoyee = nettoyer_valeur(valeur)
    
    def correspondance_proche(nom_donnee):
        # Nettoie également le nom dans les données pour une comparaison plus précise
        nom_nettoye = nettoyer_valeur(nom_donnee)
        similarite = fuzz.ratio(valeur_nettoyee, nom_nettoye)
        return similarite >= seuil_similarite
    
    if type_choix == 'forme':
        for id_forme, forme in donnee_cereales_test.formes_cereales.items():
            if correspondance_proche(forme['nom']):
                return id_forme
            
    elif type_choix == 'gout':
        for id_gout, gout in donnee_cereales_test.gouts_cereales.items():
            if correspondance_proche(gout['nom']):
                return id_gout

    return None

@app.route('/', methods=['GET', 'POST'])
def form():
    # Récupérer les formes et goûts depuis donnee_cereales_test.py
    formes = donnee_cereales_test.formes_cereales
    gouts = donnee_cereales_test.gouts_cereales

    if request.method == 'POST':
        selected_gouts = request.form.getlist('gouts')  # Liste des goûts
        print(selected_gouts)
        selected_formes = request.form.getlist('formes')  # Liste des formes
        categorie = request.form.get('categorie')  # Catégorie
        titre = request.form.get('titre')  # Titre
        couleur = request.form.get('couleur')  # Couleur

        # Vérification des goûts
        gouts_valides = set()
        erreurs = []  # Liste des erreurs pour l'affichage
        for gout in selected_gouts:
            if gout.isdigit():  # Si la valeur est un numéro, on l'ajoute directement
                gouts_valides.add(gout)
            else:
                id_gout = verifier_si_existe(gout, 'gout')
                if id_gout:
                    gouts_valides.add(str(id_gout))  # Ajouter l'ID du goût valide
                else:
                    api_limiter.wait_if_needed()
                    info_gout = ia_verif_caract(gout, "gout")
                    is_french = info_gout["is_french"] == 'True'
                    is_realistic = info_gout["is_realistic"] == 'True'
                    if not is_french:
                        erreurs.append(f"Le mot '{gout}' n'existe pas en français.")
                    elif not is_realistic:
                        erreurs.append(f"Le goût '{gout}' n'est pas réalisable.")
                    else:
                        id_caract=ajouter_valeur_caracteristique("gouts", gout)
                        ajouter_element("gouts_cereales",int(id_caract),gout.lower(),gout.lower(),0.20,info_gout["description"])
                        gouts_valides.add(str(id_caract))
                        #ajout au prestashop
                        #récup id
                        #ajouter id au donnée cereales
                        #ajouter id à la liste
                        print(f"Goût '{gout}' validé et ajouté au presta")
                        time.sleep(2)

        # Vérification des formes
        formes_valides = set()
        for forme in selected_formes:
            if forme.isdigit():
                formes_valides.add(forme)
            else:
                id_forme = verifier_si_existe(forme, 'forme')
                if id_forme:
                    formes_valides.add(str(id_forme))
                else:
                    api_limiter.wait_if_needed()
                    info_forme = ia_verif_caract(forme, "forme")
                    is_french = info_forme["is_french"] == 'True'
                    is_realistic = info_forme["is_realistic"] == 'True'
                    if not is_french:
                        erreurs.append(f"Le mot '{forme}' n'existe pas en français.")
                    elif not is_realistic:
                        erreurs.append(f"La forme '{forme}' n'est pas réalisable.")
                    else:
                        id_caract=ajouter_valeur_caracteristique("formes", forme)
                        ajouter_element("formes_cereales",int(id_caract),forme.lower(),info_forme["mot_anglais"],0.20,info_forme["description"])
                        formes_valides.add(str(id_caract))
                        print(f"Frome '{forme}' validé et ajouté au presta")
                        time.sleep(2)

        

        # Si des erreurs existent, réafficher le formulaire avec un message d'erreur
        if erreurs:
            return render_template(
                'formulaire.html',
                formes=formes,
                gouts=gouts,
                erreurs=erreurs,
                selected_gouts=selected_gouts,
                selected_formes=selected_formes,
                categorie=categorie,
                titre=titre,
                couleur=couleur
            )
        else:
            #récupérer toutes les informations
            categories=[9,int(categorie),2,3]
            caracteristique={"formes": list(map(int, formes_valides)), "gouts": list(map(int, gouts_valides))}

            api_limiter.wait_if_needed()
            infos_product = generate_cereal_info(app_creat_prompt(caracteristique, categories[1], titre))
            description = infos_product["description"]
            meta_description = infos_product["meta_description"]
            meta_title = infos_product["meta_title"]
            link_rewrite = infos_product["link_rewrite"]
            ref = generer_reference("Cereales", titre)

            # Générer les images du produit
            images_gen = generate_product_images(app_creat_prompt_img(caracteristique, categories, titre, couleur), ref)

            if len(images_gen) != 2:
                print(f"Produit {titre} : Nombre d'images insuffisant, produit non envoyé.")
                #produits_non_envoies += 1 # Incrémenter le compteur des produits non envoyés
                erreurs.append(f"Nombre d'images insuffisant pour le produit '{titre}'.")
                return render_template(
                    'formulaire.html',
                    formes=formes,
                    gouts=gouts,
                    erreurs=erreurs,
                    selected_gouts=selected_gouts,
                    selected_formes=selected_formes,
                    categorie=categorie,
                    titre=titre,
                    couleur=couleur
                )
            else:

                try:
                    product = generate_product(
                        nom=titre.capitalize(),
                        reference=ref,
                        prix=calcul_prix(caracteristique, categories, 3.5),  # Prix basé sur les caractéristiques
                        description=description,
                        meta_description=meta_description,
                        meta_title=meta_title,
                        link_rewrite=link_rewrite,
                        categories=categories,
                        attributs={"taille": [1, 2, 3]},
                        caracteristiques=caracteristique,
                        images=images_gen
                    )

                    # Ajouter le produit et afficher un message
                    result = ajouter_produit(product, "/Volumes/My Passport/melange_magique/product/imgProduit")
                    if result is None:
                        raise RuntimeError(f"Erreur lors de l'ajout du produit : Produit non ajouté correctement.")                    
                    print(f"Le mélange magique de titre '{titre}' a été ajouté au site BEHH")

                    print(f"Gouts: {gouts_valides}")
                    print(f"Formes: {formes_valides}")
                    print(f"Catégorie: {categorie}")
                    print(f"Titre: {titre}")
                    print(f"Couleur: {couleur}")
                    # Si tout réussit, afficher le résultat
                    lien = "https://www.kelloggs.fr/fr_FR/brands/rice-krispies-consumer-brand.html"
                    return render_template('resultat.html', titre=titre, lien=lien, gouts_valides=gouts_valides, formes_valides=formes_valides, categorie=categorie, couleur=couleur)

                except Exception as e:
                    # Ajouter un message d'erreur et réafficher le formulaire avec les données saisies
                    erreur = f"Une erreur est survenue lors de la génération ou de l'envoi du produit : {str(e)}"
                    erreurs.append(erreur)
                    print(erreur)  # Pour le débogage

                    return render_template(
                        'formulaire.html',
                        formes=formes,
                        gouts=gouts,
                        erreurs=erreurs,
                        selected_gouts=selected_gouts,
                        selected_formes=selected_formes,
                        categorie=categorie,
                        titre=titre,
                        couleur=couleur
                    )

    # Méthode GET ou réaffichage sans erreurs
    return render_template('formulaire.html', formes=formes, gouts=gouts, erreurs=[])




@app.route('/api_status', methods=['GET'])
def api_status():
    with api_limiter.lock:
        # Calculer le temps restant pour la prochaine réinitialisation
        minute_reset_in = max(0, int(60 - (time.time() - api_limiter.minute_start_time)))
        day_reset_in = max(0, int(86400 - (time.time() - api_limiter.day_start_time)))

        status = {
            "minute_count": api_limiter.minute_count,
            "day_count": api_limiter.day_count,
            "minute_reset_in": minute_reset_in,  # Temps restant en secondes avant réinitialisation minute
            "day_reset_in": day_reset_in  # Temps restant en secondes avant réinitialisation jour
        }

    return status



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True, use_reloader=False)

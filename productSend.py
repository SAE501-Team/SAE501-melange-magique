from dotenv import load_dotenv
import os
import json
import requests
import xml.etree.ElementTree as ET

# Charger le fichier .env
load_dotenv()

# Configuration de l'API
PS_WS_AUTH_KEY = os.getenv("API_KEY")
PS_SHOP_URL = os.getenv("API_URL")

def verifier_reponse_api(response, operation):
    if response is None:
        print(f"Erreur lors de {operation} : Pas de réponse.")
    elif response.status_code in [200, 201]:
        print(f"{operation} réussie.")
    else:
        print(f"Erreur lors de {operation} : {response.status_code} - {response.text}")


# Fonction pour appeler l'API
def call_api(endpoint, method="GET", data=None, params=None, files=None):
    headers = {"Content-Type": "application/xml"}
    url = f"{PS_SHOP_URL}{endpoint}"
    try:
        response = requests.request(
            method, url, auth=(PS_WS_AUTH_KEY, ""), data=data, params=params, headers=headers, files=files, timeout=10
        )
        response.raise_for_status()  # Vérifie les erreurs HTTP
        return response
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel API : {e}")
        return None

# Fonction pour ajouter les attributs au produit
def ajouter_attributs(product_id, attributs):
    try:
        for nom_attribut, liste_attributs in attributs.items():
            for id_attribut in liste_attributs:
                if id_attribut == 1:  # Taille 1 : +1€
                    default_on_value = ""
                    prix_combinaison = 1.00
                elif id_attribut == 2:  # Taille 2 : +3€
                    default_on_value = "1"
                    prix_combinaison = 2.10
                elif id_attribut == 3:  # Taille 3 : +5€
                    default_on_value = ""
                    prix_combinaison = 3.80

                attribut_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
                    <combination>
                        <id_product><![CDATA[{product_id}]]></id_product>
                        <ean13><![CDATA[]]></ean13>
                        <mpn><![CDATA[]]></mpn>
                        <reference><![CDATA[]]></reference>
                        <supplier_reference><![CDATA[]]></supplier_reference>
                        <price><![CDATA[{prix_combinaison}]]></price>
                        <minimal_quantity><![CDATA[1]]></minimal_quantity>
                        <default_on><![CDATA[{default_on_value}]]></default_on>
                        <associations>
                            <product_option_values nodeType="product_option_value" api="product_option_values">
                                <product_option_value>
                                    <id><![CDATA[{id_attribut}]]></id>
                                </product_option_value>
                            </product_option_values>
                        </associations>
                    </combination>
                </prestashop>"""

                # Appeler l'API pour créer la combinaison
                response = call_api("combinations", method="POST", data=attribut_xml)
                verifier_reponse_api(response, f"Ajout attribut {nom_attribut} (ID {id_attribut}) pour le produit {product_id}")

    except Exception as e:
        print(f"Erreur lors de l'ajout des attributs pour le produit {product_id} : {e}")


def generate_product_features_xml(characteristics):
    # Dictionnaire des caractéristiques et leurs IDs associés
    feature_ids = {
        "formes": 2,  # L'ID pour "formes"
        "gouts": 4,   # L'ID pour "gouts"
    }

    # Construction manuelle du XML pour éviter l'échappement
    product_features = "<product_features>"
    
    # Parcours des caractéristiques et de leurs valeurs
    for feature_name, values in characteristics.items():
        feature_id = feature_ids.get(feature_name)
        
        if feature_id:
            for value_id in values:
                product_features += f"""
                    <product_feature>
                        <id><![CDATA[{feature_id}]]></id>
                        <id_feature_value><![CDATA[{value_id}]]></id_feature_value>
                    </product_feature>
                """
    
    product_features += "</product_features>"
    return product_features.strip()

def get_product_attribute_ids(id_product):
    """
    Récupère les IDs des attributs d'un produit en fonction de son ID.
    
    :param id_product: ID du produit
    :return: Liste des ids des attributs ou message d'erreur
    """
    # Construire l'URL de la requête API pour filtrer par id_product
    url = f"/combinations?filter[id_product]={id_product}"

    # Appeler l'API pour obtenir les combinaisons du produit
    response = call_api(url, method="GET")

    # Vérifier si la requête a réussi
    if response:
        try:
            # Analyser la réponse XML
            root = ET.fromstring(response.text)

            # Extraire les ID des attributs des combinaisons
            ids = []
            for combination in root.findall(".//combination"):
                # Utiliser .get() pour récupérer l'attribut 'id' de chaque élément 'combination'
                id_attr = combination.get("id")
                if id_attr:
                    ids.append(id_attr)

            # Vérifier si des attributs ont été trouvés
            if ids:
                return ids
            else:
                return "Aucune combinaison trouvée pour ce produit."

        except Exception as e:
            print(f"Erreur lors de l'analyse de la réponse XML : {e}")
            return "Erreur de traitement de la réponse."


    else:
        return "Erreur de requête."


def get_stock_id_by_product_and_attribute(id_product, id_product_attribute):
    """
    Récupère l'ID du stock pour un produit donné et son attribut, en utilisant call_api.
    
    :param id_product: L'ID du produit
    :param id_product_attribute: L'ID de l'attribut du produit
    :return: L'ID du stock ou un message d'erreur
    """
    # Construire l'URL de la requête API pour filtrer par id_product et id_product_attribute
    url = f"/stock_availables?filter[id_product]={id_product}&filter[id_product_attribute]={id_product_attribute}"

    # Appeler la fonction call_api pour récupérer les données
    response = call_api(url, method="GET")

    # Vérifier si la réponse est valide
    if response is not None:
        try:
            # Analyser la réponse XML
            root = ET.fromstring(response.text)

            # Extraire l'ID du stock disponible
            stock_id_element = root.find(".//stock_available").get("id")
            if stock_id_element is not None:
                return stock_id_element
            else:
                return "Aucun stock disponible trouvé pour ce produit et cet attribut."
        except Exception as e:
            print(f"Erreur lors de l'analyse de la réponse XML : {e}")
            return "Erreur de traitement de la réponse."
    else:
        return "Erreur lors de la récupération des données de stock."

    

# Fonction pour mettre à jour le stock
def mise_a_jour_stock(product_id):
    id_attributes = get_product_attribute_ids(product_id)
    for id_attribute in id_attributes:
        stock_id = get_stock_id_by_product_and_attribute(product_id, id_attribute)

        try:
            stock_update_xml = f"""<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
                <stock_available>
                    <id><![CDATA[{stock_id}]]></id>
                    <id_product><![CDATA[{product_id}]]></id_product>
                    <id_product_attribute><![CDATA[{id_attribute}]]></id_product_attribute>
                    <id_shop><![CDATA[1]]></id_shop>
                    <id_shop_group><![CDATA[0]]></id_shop_group>
                    <quantity><![CDATA[14]]></quantity>
                    <depends_on_stock><![CDATA[0]]></depends_on_stock>
                    <out_of_stock><![CDATA[2]]></out_of_stock>
                </stock_available>
            </prestashop>"""

            response = call_api("stock_availables", method="PUT", data=stock_update_xml)
            verifier_reponse_api(response, f"Mise à jour du stock pour le produit {product_id}")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du stock pour le produit {product_id} : {e}")

# Fonction pour ajouter les images
def ajouter_images(product_id, produit):#, dossier_images
    num =["_1","_2"]
    """images = [
        os.path.join(dossier_images, f"{produit['reference']}_1.jpg"),
        os.path.join(dossier_images, f"{produit['reference']}_2.jpg"),
    ]"""
    for i in range(len(produit['images'])):
        try:
            img_url = f"{PS_SHOP_URL}images/products/{product_id}?ws_key={PS_WS_AUTH_KEY}"
            files = {"image": (f"{produit['reference']+num[i]}.jpg", produit['images'][i], "image/jpeg")}
            response = requests.post(img_url, files=files)
            if response.status_code not in [200, 201]:
                print(f"Erreur ajout image pour {produit['nom']} : {response.text}")
            else:
                print(f"Image ajoutée avec succès : {produit['reference']+num[i]}.jpg")
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'image {produit['reference']+num[i]}.jpg : {e}")


# Fonction pour ajouter un produit
def ajouter_produit(produit, dossier_images):
    try:
        xml_features = generate_product_features_xml(produit.get("caracteristiques", {}))
        # Construction du XML de base pour le produit
        product_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                        <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
                            <product>
                                <id_supplier><![CDATA[1]]></id_supplier>
                                <id_category_default><![CDATA[{produit["id_categories"][0]}]]></id_category_default>
                                <new><![CDATA[1]]></new>
                                <id_default_combination><![CDATA[1]]></id_default_combination>
                                <id_tax_rules_group><![CDATA[1]]></id_tax_rules_group>
                                <type><![CDATA[1]]></type>
                                <id_shop_default><![CDATA[1]]></id_shop_default>
                                <reference><![CDATA[{produit["reference"]}]]></reference>
                                <supplier_reference><![CDATA[ABCDEF]]></supplier_reference>
                                <ean13><![CDATA[]]></ean13>
                                <state><![CDATA[1]]></state>
                                <product_type><![CDATA[combinations]]></product_type>
                                <price><![CDATA[{produit["prix"]:.2f}]]></price>
                                <active><![CDATA[1]]></active>
                                <available_for_order><![CDATA[1]]></available_for_order>
                                <show_price><![CDATA[1]]></show_price>
                                <meta_description>
                                    <language id="1"><![CDATA[{produit["meta_description"]}]]></language>
                                    <language id="2"><![CDATA[{produit["meta_description"]}]]></language>
                                </meta_description>
                                <meta_keywords>
                                    <language id="1"><![CDATA[Keywords]]></language>
                                    <language id="2"><![CDATA[Keywords]]></language>
                                </meta_keywords>
                                <meta_title>
                                    <language id="1"><![CDATA[{produit["meta_title"]}]]></language>
                                    <language id="2"><![CDATA[{produit["meta_title"]}]]></language>
                                </meta_title>
                                <link_rewrite>
                                    <language id="1"><![CDATA[{produit["link_rewrite"]}]]></language>
                                    <language id="2"><![CDATA[{produit["link_rewrite"]}]]></language>
                                </link_rewrite>
                                <name>
                                    <language id="1"><![CDATA[{produit["nom"]}]]></language>
                                    <language id="2"><![CDATA[{produit["nom"]}]]></language>
                                </name>
                                <description>
                                    <language id="1"><![CDATA[{produit["description"]}]]></language>
                                    <language id="2"><![CDATA[{produit["description"]}]]></language>
                                </description>
                                <description_short>
                                    <language id="1"><![CDATA[{produit["description"][:100]}...]]></language>
                                    <language id="2"><![CDATA[{produit["description"][:100]}...]]></language>
                                </description_short>
                                <associations>
                                    <categories>"""
        
        # Ajouter toutes les catégories dans la section <categories>
        for category_id in produit["id_categories"]:
            product_xml += f"""
                                        <category>
                                            <id><![CDATA[{category_id}]]></id>
                                        </category>"""
        
        # Ajouter le reste des sections du produit
        product_xml += f"""
                                    </categories>
                                    {xml_features}
                                </associations>
                            </product>
                        </prestashop>"""

        # Envoi du produit
        response = call_api("products", method="POST", data=product_xml)
        if response is None or response.status_code not in [200, 201]:
            print(f"Erreur lors de l'ajout du produit {produit['nom']} : {response.text if response else 'Pas de réponse'}")
            return None

        product_id = ET.fromstring(response.text).find(".//product/id").text
        print(f"Produit ajouté : {produit['nom']} avec ID {product_id}")

        # Ajout des attributs et caractéristiques
        ajouter_attributs(product_id, produit.get("attributs", {}))

        # Mise à jour du stock pour le produit
        mise_a_jour_stock(product_id)

        # Gestion des images
        ajouter_images(product_id, produit)#, dossier_images

    except Exception as e:
        print(f"Erreur inattendue lors de l'ajout du produit {produit['nom']} : {e}")


# Lecture des produits depuis un fichier JSON
"""def importer_produits():
    try:
        with open("./product/produits.json", "r") as file:
            produits = json.load(file)

        dossier_images = "./product/imgProduit"

        for produit in produits:
            ajouter_produit(produit, dossier_images)
    except FileNotFoundError:
        print("Le fichier produits.json est introuvable.")
    except json.JSONDecodeError as e:
        print(f"Erreur de lecture du fichier JSON : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    importer_produits()"""

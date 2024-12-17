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

# Fonction pour ajouter un produit
def ajouter_produit(produit, dossier_images):
    try:
        # Construction du XML de base pour le produit
        product_xml = f"""<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
            <product>
                <id_supplier><![CDATA[1]]></id_supplier>
                <id_category_default><![CDATA[{produit["id_categories"][0]}]]></id_category_default>
                <new><![CDATA[1]]></new>
                <id_tax_rules_group><![CDATA[1]]></id_tax_rules_group>
                <type><![CDATA[1]]></type>
                <id_shop_default><![CDATA[1]]></id_shop_default>
                <reference><![CDATA[{produit["reference"]}]]></reference>
                <supplier_reference><![CDATA[ABCDEF]]></supplier_reference>
                <state><![CDATA[1]]></state>
                <product_type><![CDATA[standard]]></product_type>
                <price><![CDATA[{produit["prix"]}]]></price>
                <unit_price><![CDATA[{produit["prix"]}]]></unit_price>
                <active><![CDATA[1]]></active>
                <meta_description>
                    <language id="2"><![CDATA[{produit["description"]}]]></language>
                </meta_description>
                <meta_keywords>
                    <language id="2"><![CDATA[Keywords]]></language>
                </meta_keywords>
                <meta_title>
                    <language id="2"><![CDATA[{produit["nom"]}]]></language>
                </meta_title>
                <link_rewrite>
                    <language id="2"><![CDATA[awesome-product]]></language>
                </link_rewrite>
                <name>
                    <language id="2"><![CDATA[{produit["nom"]}]]></language>
                </name>
                <description>
                    <language id="2"><![CDATA[{produit["description"]}]]></language>
                </description>
                <description_short>
                    <language id="2"><![CDATA[{produit["description"][:100]}]]></language>
                </description_short>
                <associations>
                    <categories>
                        <category>
                            <id><![CDATA[{produit["id_categories"][0]}]]></id>
                        </category>
                    </categories>
                </associations>
            </product>
        </prestashop>"""

        # Envoi du produit
        response = call_api("products", method="POST", data=product_xml)
        if response is None or response.status_code not in [200, 201]:
            print(f"Erreur lors de l'ajout du produit {produit['nom']} : {response.text if response else 'Pas de réponse'}")
            return None

        product_id = ET.fromstring(response.text).find("./product/id").text
        print(f"Produit ajouté : {produit['nom']} avec ID {product_id}")

        # Mise à jour du stock pour le produit
        mise_a_jour_stock(product_id)

        # Gestion des catégories supplémentaires
        for id_categorie in produit["id_categories"][1:]:
            category_data = f"""<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
                <product>
                    <id><![CDATA[{product_id}]]></id>
                    <price><![CDATA[{produit["prix"]}]]></price>
                    <associations>
                        <categories>
                            <category>
                                <id><![CDATA[{id_categorie}]]></id>
                            </category>
                        </categories>
                    </associations>
                </product>
            </prestashop>"""

            cat_response = call_api(f"products/{product_id}", method="PUT", data=category_data)
            verifier_reponse_api(cat_response, f"Ajout catégorie {id_categorie} pour le produit {produit['nom']}")

        # Gestion des images
        ajouter_images(product_id, produit, dossier_images)

    except Exception as e:
        print(f"Erreur inattendue lors de l'ajout du produit {produit['nom']} : {e}")

# Fonction pour mettre à jour le stock
def mise_a_jour_stock(product_id):
    try:
        # Récupération de l'entité stock disponible
        stock_url = f"stock_availables?filter[id_product]={product_id}&display=full"  # Correction de l'URL
        response = call_api(stock_url, method="GET")
        if response is None:
            print(f"Erreur lors de la récupération du stock pour le produit {product_id}")
            return

        # Extraction de l'ID du stock
        root = ET.fromstring(response.text)
        stock_id = root.find(".//stock_available/id").text

        # Mise à jour du stock
        stock_update_xml = f"""<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
            <stock_available>
                <id><![CDATA[{stock_id}]]></id>
                <quantity><![CDATA[40]]></quantity>
            </stock_available>
        </prestashop>"""

        stock_update_url = f"stock_availables/{stock_id}"  # URL de mise à jour du stock
        stock_update_response = call_api(stock_update_url, method="PATCH", data=stock_update_xml)
        verifier_reponse_api(stock_update_response, f"Mise à jour du stock pour le produit {product_id}")

    except Exception as e:
        print(f"Erreur lors de la mise à jour du stock pour le produit {product_id} : {e}")


# Fonction pour ajouter les images
def ajouter_images(product_id, produit, dossier_images):
    images = [
        os.path.join(dossier_images, f"{produit['reference']}_1.jpg"),
        os.path.join(dossier_images, f"{produit['reference']}_2.jpg"),
    ]

    for img_path in images:
        if os.path.exists(img_path):
            try:
                with open(img_path, "rb") as img_file:
                    img_url = f"{PS_SHOP_URL}images/products/{product_id}?ws_key={PS_WS_AUTH_KEY}"
                    files = {"image": (os.path.basename(img_path), img_file, "image/jpeg")}
                    response = requests.post(img_url, files=files)
                    if response.status_code not in [200, 201]:
                        print(f"Erreur ajout image pour {produit['nom']} : {response.text}")
                    else:
                        print(f"Image ajoutée avec succès : {img_path}")
            except Exception as e:
                print(f"Erreur lors de l'ajout de l'image {img_path} : {e}")
        else:
            print(f"Image non trouvée : {img_path}")

# Lecture des produits depuis un fichier JSON
def importer_produits():
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
    importer_produits()

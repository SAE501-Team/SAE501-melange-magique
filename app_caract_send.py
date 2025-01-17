from dotenv import load_dotenv
import os
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
    
def ajouter_valeur_caracteristique(feature, valeur):
    """
    Fonction pour ajouter une nouvelle valeur à une caractéristique d'un produit via l'API et récupérer l'ID de la valeur ajoutée.

    :param feature: Le nom de la caractéristique à laquelle ajouter la valeur (ex. "formes", "gouts")
    :param valeur: La valeur à ajouter à la caractéristique, qui sera utilisée dans les langues définies
    :return: L'ID de la valeur de caractéristique ajoutée ou None en cas d'erreur
    """
    feature_ids = {
        "formes": 2,  # L'ID pour "formes"
        "gouts": 4,   # L'ID pour "gouts"
    }

    try:
        valeur = valeur.capitalize()  # Assurez-vous que la première lettre est en majuscule

        # Construction du XML pour ajouter une nouvelle valeur de caractéristique
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
        <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
            <product_feature_value>
                <id><![CDATA[]]></id>
                <id_feature><![CDATA[{feature_ids[feature]}]]></id_feature>
                <custom><![CDATA[]]></custom>
                <value>
                    <language id="1"><![CDATA[{valeur}]]></language>
                    <language id="2"><![CDATA[{valeur}]]></language>
                </value>
            </product_feature_value>
        </prestashop>"""

        # Appel de l'API pour ajouter la valeur de caractéristique
        response = call_api("product_feature_values", method="POST", data=xml_data)

        # Vérification de la réponse de l'API
        if response is None or response.status_code not in [200, 201]:
            print(f"Erreur lors de l'ajout de la valeur à la caractéristique {feature} : {response.text if response else 'Pas de réponse'}")
            return None  # Retourner None si une erreur se produit
        else:
            print(f"Valeur '{valeur}' ajoutée avec succès à la caractéristique {feature}.")

            # Analyser la réponse XML pour récupérer l'ID de la nouvelle valeur de caractéristique
            try:
                root = ET.fromstring(response.text)
                # Extraire l'ID de la valeur de caractéristique
                feature_value_id = root.find(".//product_feature_value/id").text
                print(f"L'ID de la nouvelle valeur de caractéristique est : {feature_value_id}")
                return feature_value_id  # Retourner l'ID de la nouvelle valeur de caractéristique
            except Exception as e:
                print(f"Erreur lors de l'analyse de la réponse XML : {e}")
                return None

    except Exception as e:
        print(f"Erreur inattendue lors de l'ajout de la valeur '{valeur}' à la caractéristique {feature} : {e}")
        return None

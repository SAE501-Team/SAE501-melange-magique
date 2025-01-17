from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import ast

load_dotenv()

def generate_cereal_info(prompt):
    """
    Génère des informations pour une boîte de céréales à partir d'un prompt donné.

    :param api_key: Clé API Google utilisée pour configurer l'API Generative AI.
    :param prompt: Le texte de l'invite pour générer des informations.
    :return: Un dictionnaire contenant les informations extraites ou un message d'erreur.
    """
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

        # Créer un modèle de génération de texte
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Générer le contenu
        response = model.generate_content(prompt)

        if hasattr(response, 'text') and response.text:
            print("Donnée de base :", response.text)

            cleaned_text = response.text.strip()  # Supprimer les espaces ou retours à la ligne autour
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.lstrip("```python").lstrip("```json").strip("```")

            print("Donnée cleaned :", cleaned_text)

            # Vérifier si la chaîne finit encore par ``` et supprimer
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            print("Donnée cleaned finale :", cleaned_text)

            # Convertir en liste ou JSON
            try:
                response_data = ast.literal_eval(cleaned_text)
                print("Donnée finale :", response_data)
            except Exception as e:
                print("Erreur lors de la conversion :", str(e))

            # Extraire les informations
            return {
                "is_french": response_data[0],
                "is_realistic": response_data[1],
                "mot_anglais": response_data[2],
                "description": response_data[3],
            }
        else:
            return {"error": "La réponse est vide ou invalide."}
    except json.JSONDecodeError as e:
        return {"error": f"Erreur lors de la conversion en JSON : {str(e)}"}
    except Exception as e:
        return {"error": f"Une erreur s'est produite : {str(e)}"}
    

def ia_verif_caract(mot,type):
    if type == "gout":
        prompt="Génère des informations pour ce mot : "+mot+". Je veux que tu me le génère sous cette forme : ['True si le mot est français sinon False','True si cela correspond à une chose qui a un goût mangeable sinon False','le mot en anglais','une description d'a quoi ressemble visuellement une cereale de ce gout en anglais avec une dizaine de mots']"
    elif type == "forme":
        prompt="Génère des informations pour ce mot : "+mot+". Je veux que tu me le génère sous cette forme : ['True si le mot est français sinon False','True si ce mot peut avoir une forme réalisable en céréale : une forme simple, bien définie, et reconnaissable sinon False','le mot en anglais','une description d'a quoi ressemble visuellement une cereale de cette forme en anglais avec une dizaine de mots']"

    return generate_cereal_info(prompt)

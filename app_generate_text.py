from dotenv import load_dotenv
import google.generativeai as genai
import os
import json

load_dotenv()

def generate_cereal_info(prompt):
    """
    Génère des informations pour une boîte de céréales à partir d'un prompt donné.

    :param api_key: Clé API Google utilisée pour configurer l'API Generative AI.
    :param prompt: Le texte de l'invite pour générer des informations.
    :return: Un dictionnaire contenant les informations extraites ou un message d'erreur.
    """
    try:
        # Spécifiez explicitement le chemin du fichier .env
        dotenv_path = '/var/www/melange_magique/.env'
        load_dotenv(dotenv_path=dotenv_path)

        # Vérifier si la clé a bien été chargée
        print(os.getenv('GOOGLE_API_KEY'))
        print("avant d'essayer de recup la google api key")
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

        # Créer un modèle de génération de texte
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Générer le contenu
        response = model.generate_content(prompt)

        if hasattr(response, 'text') and response.text:

            # Nettoyer la réponse
            cleaned_text = response.text.strip('```json')[:-4]  # Suppression des derniers caractères inutiles

            # Reformater le contenu en JSON
            valid_json_text = cleaned_text.replace("\n", "").replace("  ", "").strip()
            response_data = json.loads(valid_json_text)

            # Extraire les informations
            return {
                "description": response_data[0],
                "meta_description": response_data[1],
                "meta_title": response_data[2],
                "link_rewrite": response_data[3],
            }
        else:
            return {"error": "La réponse est vide ou invalide."}
    except json.JSONDecodeError as e:
        return {"error": f"Erreur lors de la conversion en JSON : {str(e)}"}
    except Exception as e:
        return {"error": f"Une erreur s'est produite : {str(e)}"}
    




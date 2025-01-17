from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
import time
from io import BytesIO

load_dotenv()

def generate_product_image(prompt, product_ref, max_retries=3):
    """
    Génère une image basée sur un prompt et nomme le fichier avec la référence produit.

    :param prompt: La description textuelle de l'image à générer.
    :param product_ref: La référence unique du produit qui sera utilisée pour nommer le fichier.
    """
    # Configuration
    api_key_img = os.getenv('API_KEY_IMG')
    if not api_key_img:
        print("Erreur : Clé API non trouvée.")
    output_dir = "/Volumes/My Passport/generated_send_user_BEHH/product/imgProduit"

    # Créer le répertoire si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    
    # Définir le chemin complet de sortie pour le fichier image
    output_file = os.path.join(output_dir, f"{product_ref}.png")

    # Initialiser le client Hugging Face
    try:
        client = InferenceClient("stabilityai/stable-diffusion-3.5-large", token=api_key_img)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du client : {e}")
        return

    # Générer l'image
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Tentative génération d'image {attempt} sur {max_retries}...")
            image = client.text_to_image(prompt)
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")  # Sauvegarder l'image au format JPEG dans l'objet en mémoire
            image_bytes.seek(0)
            #image.save(output_file)
            print(f"Image {product_ref}.png généré.")
            #print(f"Image sauvegardée sous : {output_file}")
            return  image_bytes
        except Exception as e:
            print(f"Erreur lors de la génération ou de la sauvegarde de l'image (tentative {attempt}) : {e}")
            if attempt < max_retries:
                print("Nouvelle tentative dans 15 secondes...")
                time.sleep(15)  # Attendre 2 secondes avant de réessayer
            else:
                print("Échec après plusieurs tentatives. Abandon.")
                return

# Exemple d'utilisation

def generate_product_images(prompts, ref):
    num =["_1","_2"]
    images_gen=[]
    for i in range(len(prompts)):
        images_gen.append(generate_product_image(prompt=prompts[i], product_ref=ref+num[i]))
    return images_gen

#pr="A cereal box design which takes the whole picture with cereals in the shape of petal and stiks with a plain (beige in color), chocolate (brown in color) and hazelnut (light brown in color) flavor. The box shows 'Starsette' in bold letters, surrounded by natural elements like wheat stalks, green leaves, and a rustic background. The design emphasizes organic and eco-friendly vibes, with earthy tones and minimalist, clean typography. It highlights '100% Organic' and 'No Artificial Additives' prominently, with a small eco-label and recycling icon on the side."
#generate_product_image(prompt=pr, product_ref="test1")

# prompt gourmand : A cereal box design which takes the whole picture with cereals in the shape of ball and stick with a chocolate (brown in color) and honey (yellow in color) flavor. The box shows 'Honey Choco Crunch' in bold letters, with milk splashes around the cereal balls. The design is colorful, modern, and nutritional info on the side. The style is bright, playful, and family-friendly.
# prompt bio : A cereal box design which takes the whole picture with cereals in the shape of petal and star with a plain (beige in color), chocolate (brown in color) and hazelnut (light brown in color) flavor. The box shows 'Starsette' in bold letters, surrounded by natural elements like wheat stalks, green leaves, and a rustic background. The design emphasizes organic and eco-friendly vibes, with earthy tones and minimalist, clean typography. It highlights '100% Organic' and 'No Artificial Additives' prominently, with a small eco-label and recycling icon on the side.
# prompt sportif : A cereal box design which takes the whole picture with cereals in the shape of petal and star with a plain (beige in color), chocolate (brown in color) and hazelnut (light brown in color) flavor. The box shows 'Starsette' in bold letters, with a dynamic background featuring motion lines and an athlete in action. The design uses bold colors, symbolizing energy. Highlights include 'Boost Your Energy' and 'High in Protein' for a sleek, sporty look.

import google.generativeai as genai
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyCpgmSu-8PPPpqlnLqBlp3nTJCxBuZhV5U"


# Configurez votre clé API Google
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])  # Remplacez par votre clé API

# Créez un modèle de génération de texte Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Prompt pour générer du texte
prompt = "Génère des informations pour une boite de cereal de catégorie bio, de goût chocolat et venille, en forme de pétale. Sachant que c'est pour un site de e-commerce qui vend des céréales. Je veux que tu me le génère sous cette forme : ['nom Produit créatif pas trop long','description','meta_description','meta_title en lien avec le nom du produit','link_rewrite (nom-du-produit)]"

# Générer le contenu
response = model.generate_content(prompt)

# Afficher le texte généré
print(response.text)


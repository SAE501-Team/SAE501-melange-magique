from diffusers import StableDiffusionPipeline
import torch
from datetime import datetime
from PIL import Image

# Charger le pipeline de Stable Diffusion avec des optimisations
model_id = "CompVis/stable-diffusion-v1-4"  # Modèle Stable Diffusion
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, 
    torch_dtype=torch.float16  # Réduit la mémoire utilisée et accélère sur GPU
)

# Activer les optimisations pour la mémoire
pipe.enable_attention_slicing()  # Réduit la mémoire nécessaire pour le GPU
try:
    pipe.enable_xformers_memory_efficient_attention()  # Accélération supplémentaire (si compatible)
except Exception as e:
    print("Attention slicing activé, mais Xformers non supporté :", e)

# Utiliser MPS pour le GPU Apple Silicon ou CPU si non disponible
device = "mps" if torch.backends.mps.is_available() else "cpu"
pipe.to(device)

# Charger une image de référence
image_path1 = "images_reference/imageChoc.png"  # Chemin vers votre image de référence
image_path = "images_reference/bouleChocoCereal.webp"
init_image = Image.open(image_path).convert("RGB").resize((512, 352))  # Redimensionner l'image


# Prompt pour générer une image prompte boite de cereal 
prompt1 = (
    "A colorful cereal poster design which takes the whole picture with round chocolate and honey flavored cereal balls. The box shows 'Honey Choco Crunch' in bold letters, with milk splashes around the cereal balls. The chocolate balls are dark brown, and the honey ones are yellow. The design is modern, and nutritional info on the side. The style is bright, playful, and family-friendly."
)
# Prompte cereales
prompt = (
    "Create a high-quality image of the front of a cereal box for a fictional brand called 'Crispy Crunch'. The design should cover the entire front of the box, with bold and colorful graphics. The box should feature a large, eye-catching logo at the top with a modern, playful font. Below the logo, show a large bowl filled with crispy cereal and vibrant fruit pieces, like red berries and yellow banana slices, with some milk splashing around. The background should be a bright, clean color, and the design should feel fresh, fun, and appealing to a wide audience. Make sure the image fills the entire frame, showcasing the front of the box."
)

# Générer l'image avec un nombre réduit de steps et une résolution de sortie adaptée
image = pipe(prompt=prompt, image=init_image, strength=0.3, guidance_scale=7.5, num_inference_steps=50, height=512, width=352).images[0]

# Générer un nom de fichier unique basé sur la date et l'heure
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"resultats/generated_image_{timestamp}.png"

# Sauvegarder l'image avec le nom unique
image.save(filename)
print(f"Image générée et sauvegardée sous : {filename}")


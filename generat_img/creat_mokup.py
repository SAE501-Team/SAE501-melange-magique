import cv2
from PIL import Image, ImageDraw
import numpy as np

def round_corners(image_path, radius):
    """
    Fonction pour arrondir les angles d'une image.
    Args:
        image_path: chemin de l'image à arrondir
        radius: rayon de l'arrondi (en pixels)
    Returns:
        Une image PIL avec coins arrondis.
    """
    # Charger l'image
    image = Image.open(image_path).convert("RGBA")  # Assurez-vous d'utiliser le mode RGBA (transparence)

    # Créer un masque arrondi
    mask = Image.new("L", image.size, 0)  # "L" pour un masque en niveaux de gris
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)

    # Appliquer le masque à l'image
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))  # Créer une image transparente
    result.paste(image, (0, 0), mask=mask)

    return result

# Charger l'image de la boîte de céréales existante
box_image_path = "images_reference/mokupCereal.png"  # Chemin de l'image existante
new_design_path_brute = "resultats/generated_image_20241217_103054.png"  # Chemin du nouveau design

# Appliquer l'arrondi aux coins du nouveau design
rounded_design = round_corners(new_design_path_brute, radius=10)

# Convertir l'image PIL en tableau NumPy pour OpenCV
new_design = np.array(rounded_design)

# Charger l'image originale avec OpenCV
original_image = cv2.imread(box_image_path, cv2.IMREAD_UNCHANGED)

# Si l'image originale n'a pas de canal alpha, en ajouter un
if original_image.shape[2] == 3:
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2BGRA)


# Redimensionner le nouveau design
design_height, design_width = 274, 209  # Taille souhaitée
new_design_resized = cv2.resize(new_design, (design_width, design_height), interpolation=cv2.INTER_AREA)

# Définir la position pour coller le design
x_offset, y_offset = 132, 76

# Extraire les canaux de l'image redimensionnée
new_design_rgb = new_design_resized[:, :, :3]  # RGB uniquement
new_design_alpha = new_design_resized[:, :, 3]  # Canal alpha

# Extraire la région d'intérêt (ROI) dans l'image originale
roi = original_image[y_offset:y_offset + design_height, x_offset:x_offset + design_width]

# Combiner l'alpha du design avec la région originale
for c in range(3):  # Pour les canaux B, G, R
    roi[:, :, c] = roi[:, :, c] * (1 - new_design_alpha / 255.0) + \
                   new_design_rgb[:, :, c] * (new_design_alpha / 255.0)

# Remplacer la région modifiée dans l'image originale
original_image[y_offset:y_offset + design_height, x_offset:x_offset + design_width] = roi

# Sauvegarder l'image finale
output_path = "output_image_with_transparency.png"
cv2.imwrite(output_path, original_image)

# Afficher le résultat
Image.open(output_path).show()

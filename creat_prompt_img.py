from donnee_cereales import formes_cereales, gouts_cereales, categorie_cereales

def creat_prompt_img_cereals(caracteristic, categories):
    def format_list(items):
        if len(items) > 1:
            return ", ".join(items[:-1]) + " and " + items[-1]
        elif items:
            return items[0]
        return ""

    # Retrieve shape names and descriptions
    shapes = [
        formes_cereales.get(shape_id, {}).get("nom_anglais", "") + ": " + formes_cereales.get(shape_id, {}).get("description", "")
        for shape_id in caracteristic.get("formes", [])
    ]

    # Retrieve taste names and descriptions
    tastes = [
        gouts_cereales.get(taste_id, {}).get("nom_anglais", "") + ": " + gouts_cereales.get(taste_id, {}).get("description", "")
        for taste_id in caracteristic.get("gouts", [])
    ]

    # Format the shapes and tastes
    shapes_str = format_list([f for f in shapes if f])
    tastes_str = format_list([t for t in tastes if t])

    # Generate the cereal appearance description
    appearance_description = f"Looking down at the 'Starsette' cereal, you will see the entire area covered with cereals in the shape of {shapes_str}. "
    appearance_description += f"These cereals have a {tastes_str} flavor, filling every part of the space. The surface is densely packed with cereals, each shape contributing to a harmonious and full texture. "

    # Category-specific descriptions
    if 11 in categories:  # Gourmand
        appearance_description += "The cereals have rich, indulgent textures and warm hues, like chocolate and hazelnut. "
        appearance_description += "Their shapes resemble delicate petals and playful stars, filling the space with a warm and inviting appearance."

    if 12 in categories:  # Sport
        appearance_description += "The cereals have an energetic, dynamic presence, with sleek and bold shapes, filling the surface. "
        appearance_description += "The layout is vibrant and active, symbolizing power and performance."

    if 13 in categories:  # Bio
        appearance_description += "The cereals exude a natural, earthy aesthetic, with soft, curved shapes covering the entire area. "
        appearance_description += "Their light beige and brown colors reflect organic ingredients, filling the space with wholesome energy."

    return appearance_description

def creat_prompt_img_box(caracteristique, categories, name):

    def format_list(items):
        if len(items) > 1:
            return ", ".join(items[:-1]) + " and " + items[-1]
        elif items:
            return items[0]
        return ""

    # Récupérer les noms des formes
    formes = [
        formes_cereales.get(forme_id, {}).get("nom_anglais", "")
        for forme_id in caracteristique.get("formes", [])
    ]

    # Récupérer les noms des goûts
    gouts = [
        gouts_cereales.get(gout_id, {}).get("nom_anglais", "")
        for gout_id in caracteristique.get("gouts", [])
    ]

    # Construire les chaînes formatées
    formes_str = format_list([f for f in formes if f])
    gouts_str = format_list([g for g in gouts if g])
    prompt_gen = ""

    if 11 in categories:
        prompt_gen = "A cereal box design which takes the whole picture with cereals in the shape of "+formes_str+" with a "+gouts_str+" flavor. The box shows '"+name+"' in bold letters, with milk splashes around the cereal. The design is colorful, modern, and nutritional info on the side. The style is bright, playful, and family-friendly."

    if 12 in categories:
        prompt_gen = "A cereal box design which takes the whole picture with cereals in the shape of "+formes_str+" with a "+gouts_str+" flavor. The box shows '"+name+"' in bold letters, with a dynamic background featuring motion lines and an athlete in action. The design uses bold colors, symbolizing energy. Highlights include 'Boost Your Energy' and 'High in Protein' for a sleek, sporty look."

    if 13 in categories:
        prompt_gen = "A cereal box design which takes the whole picture with cereals in the shape of "+formes_str+" with a "+gouts_str+" flavor. The box shows '"+name+"' in bold letters, surrounded by natural elements like wheat stalks, green leaves, and a rustic background. The design emphasizes organic and eco-friendly vibes, with earthy tones and minimalist, clean typography. It highlights '100% Organic' and 'No Artificial Additives' prominently, with a small eco-label and recycling icon on the side."

    return prompt_gen

# caracteristiques = {'formes': [10, 21], 'gouts': [23, 28, 34]}
# categories = [5]
# name = "Starsette"


def creat_prompt_img(caracteristiques, categories, name):
    # Création des prompts à l'aide des fonctions existantes
    prompt_box = creat_prompt_img_box(caracteristiques, categories, name)
    prompt_cereals = creat_prompt_img_cereals(caracteristiques, categories)

    if prompt_box and prompt_cereals:
        print("Prompt créé")
        
    return [prompt_box, prompt_cereals]



# prompt gourmand : A cereal box design which takes the whole picture with cereals in the shape of ball and stick with a chocolate (brown in color) and honey (yellow in color) flavor. The box shows 'Honey Choco Crunch' in bold letters, with milk splashes around the cereal balls. The design is colorful, modern, and nutritional info on the side. The style is bright, playful, and family-friendly.
# prompt bio : A cereal box design which takes the whole picture with cereals in the shape of petal and star with a plain (beige in color), chocolate (brown in color) and hazelnut (light brown in color) flavor. The box shows 'Starsette' in bold letters, surrounded by natural elements like wheat stalks, green leaves, and a rustic background. The design emphasizes organic and eco-friendly vibes, with earthy tones and minimalist, clean typography. It highlights '100% Organic' and 'No Artificial Additives' prominently, with a small eco-label and recycling icon on the side.
# prompt sportif : A cereal box design which takes the whole picture with cereals in the shape of petal and star with a plain (beige in color), chocolate (brown in color) and hazelnut (light brown in color) flavor. The box shows 'Starsette' in bold letters, with a dynamic background featuring motion lines and an athlete in action. The design uses bold colors, symbolizing energy. Highlights include 'Boost Your Energy' and 'High in Protein' for a sleek, sporty look.




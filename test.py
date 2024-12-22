import pprint
import ast

# Fonction pour ajouter une nouvelle forme ou un nouveau goût
def ajouter_element(type_element, id_element, nom, nom_anglais, prix, description):
    file_path = "/Volumes/My Passport/generated_send_user_BEHH/donnee_cereales_test.py"

    # Lire tout le contenu du fichier source
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Trouver les indices de début et de fin pour la section spécifiée (formes_cereales ou gouts_cereales)
    start_index = None
    end_index = None
    bracket_count = 0  # Compte les accolades pour identifier correctement la fin du dictionnaire
    for i, line in enumerate(lines):
        if f"{type_element} = {{" in line:  # Début de la section
            start_index = i
            bracket_count += line.count("{")
        elif start_index is not None:
            bracket_count += line.count("{") - line.count("}")
            if bracket_count == 0:  # Fin du dictionnaire
                end_index = i
                break

    # Vérifier que la section a bien été trouvée
    if start_index is None or end_index is None:
        raise ValueError(f"La section '{type_element}' est introuvable ou mal formée dans le fichier.")

    # Extraire et analyser la définition actuelle de l'élément (formes_cereales ou gouts_cereales)
    element_code = lines[start_index:end_index + 1]
    element_str = "".join(f.split("#")[0].strip() for f in element_code)  # Supprimer les commentaires

    try:
        element_dict = ast.literal_eval(f"{element_str.split('=', 1)[1].strip()}")
    except Exception as e:
        print("Erreur dans la chaîne analysée :")
        print(f"{element_str}")
        raise ValueError(f"Erreur d'analyse du dictionnaire {type_element} : {e}")

    # Modifier le dictionnaire
    element_dict[id_element] = {
        "nom": nom,
        "nom_anglais": nom_anglais,
        "prix": prix,
        "description": description
    }

    # Reconstruire la définition du dictionnaire en texte formaté
    element_code_new = pprint.pformat(element_dict, width=120, compact=False)
    element_code_new = [f"{type_element} = {element_code_new}\n"]

    # Réinsérer le contenu modifié dans les lignes d'origine
    lines = lines[:start_index] + element_code_new + lines[end_index + 1:]

    # Écrire les modifications dans le fichier source
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)

    print(f"La section '{type_element}' a été mise à jour avec succès.")

# Exemple d'utilisation pour ajouter une forme
ajouter_element(
    "formes_cereales",
    19,
    "test",
    "test",
    0.01,
    "Just a test shape."
)

# Exemple d'utilisation pour ajouter un goût
ajouter_element(
    "gouts_cereales",
    35,
    "nouveau goût",
    "new flavor",
    0.25,
    "A brand new flavor for testing."
)

from generat_info_product import generate_products

def main():
    # Demander à l'utilisateur combien de produits il veut générer
    number_of_products = int(input("Combien de produits voulez-vous générer ? "))

    # Appeler la fonction pour générer la liste de produits
    products = generate_products(number_of_products)

    # Afficher la liste de produits
    for product in products:
        print(product)

if __name__ == "__main__":
    main()


from binance_client import get_all_binance_symbols, get_tradable_usdc_pairs

if __name__ == "__main__":
    print("Récupération de tous les symboles disponibles sur Binance...")
    all_symbols_list = get_all_binance_symbols()

    if all_symbols_list:
        print(f"Succès! Nombre total de symboles trouvés : {len(all_symbols_list)}")
        print("Voici quelques exemples :", all_symbols_list[:5])
        print("-" * 50)

    print("Récupération de toutes les paires USDC actuellement tradables...")
    usdc_symbols_list = get_tradable_usdc_pairs()

    if usdc_symbols_list:
        print(f"Succès! Nombre de paires USDC tradables trouvées : {len(usdc_symbols_list)}")
        print("Voici quelques exemples :", usdc_symbols_list[:5])
        print("-" * 50)
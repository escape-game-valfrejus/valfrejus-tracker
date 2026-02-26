import os
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # On lance le navigateur
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Ton nouveau lien direct
        url = "https://valfrejus.digisnow.app/map/1/fr?fullscreen=true"
        
        try:
            print(f"Connexion à {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # On attend que les données météo/pistes soient chargées
            page.wait_for_timeout(10000) 

            # Fonctions pour extraire le statut
            # Le site utilise souvent des classes CSS ou des attributs 'data-id'
            def get_status(asset_id):
                # On cherche l'élément qui a l'ID de la remontée
                # Dans ton JSON, Arrondaz = 1991 et Punta Bagna = 1994 (ou 2010 selon le picto)
                # On va essayer de trouver l'élément par son ID d'asset
                try:
                    # On cherche la pastille de couleur associée à l'asset
                    selector = f"text={asset_id}" 
                    # Note: Si le sélecteur texte ne marche pas, on peut chercher le rond de couleur
                    # Mais le plus simple est de regarder le statut dans la liste si elle existe
                    return "OPEN" # Par défaut pour le test
                except:
                    return "CLOSED"

            # Mise à jour pour tes deux remontées
            # On va créer un fichier JSON simple pour l'ESP32
            # TCD Arrondaz (ID 1991) / TSD Punta Bagna (ID 2010 ou 1994)
            
            # ASTUCE : Pour debugger, on prend une photo
            page.screenshot(path="debug_map.png")
            
            # Pour l'instant on écrit un statut fixe pour tester la communication
            # Je vais te donner une méthode encore plus précise si tu me confirmes 
            # que 'debug_map.png' montre bien les pastilles.
            
            status_text = "ARRONDAZ:OPEN\nPUNTA_BAGNA:OPEN"
            
            with open("status.txt", "w") as f:
                f.write(status_text)
                
            print("Scan terminé avec succès.")

        except Exception as e:
            print(f"Erreur : {e}")
            with open("status.txt", "w") as f:
                f.write("ERROR")

        browser.close()

if __name__ == "__main__":
    run()

import os
from playwright.sync_api import sync_playwright
from PIL import Image

def run():
    with sync_playwright() as p:
        # On augmente la taille de la fenêtre pour capter le haut
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1500} # On passe à 1500 de haut
        )
        page = context.new_page()

        # URL directe plein écran
        url = "https://valfrejus.digisnow.app/map/1/fr?fullscreen=true"
        
        try:
            print(f"Connexion à {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # On attend 15 secondes que TOUT le domaine s'affiche
            page.wait_for_timeout(15000) 

            # Screenshot complet pour vérification
            screenshot_path = "debug_map.png"
            page.screenshot(path=screenshot_path)

            # Analyse des pixels
            img = Image.open(screenshot_path)
            
            # --- ANALYSE ARRONDAZ (ID 1991) ---
            # Coordonnées à ajuster selon ton image reçue
            pix_arrondaz = img.getpixel((534, 905)) 
            status_arrondaz = "OPEN" if pix_arrondaz[1] > 150 else "CLOSED"
            
            # --- ANALYSE PUNTA BAGNA (ID 2010) ---
            # ICI : Il faudra me donner les coordonnées X,Y 
            # quand tu verras le haut de la carte sur l'image !
            # Pour l'instant on met des coordonnées probables (ex: 1005, 403)
            pix_punta = img.getpixel((1005, 403)) 
            status_punta = "OPEN" if pix_punta[1] > 150 else "CLOSED"

            # On crée le fichier de statut pour l'ESP32
            # Format simple : ARRONDAZ:1,PUNTA:1 (1=Ouvert, 0=Fermé)
            res_arr = "1" if status_arrondaz == "OPEN" else "0"
            res_pun = "1" if status_punta == "OPEN" else "0"
            
            with open("status.txt", "w") as f:
                f.write(f"A:{res_arr},P:{res_pun}")
                
            print(f"Résultats -> Arrondaz: {status_arrondaz}, Punta: {status_punta}")

        except Exception as e:
            print(f"Erreur : {e}")
            with open("status.txt", "w") as f:
                f.write("A:0,P:0")

        browser.close()

if __name__ == "__main__":
    run()

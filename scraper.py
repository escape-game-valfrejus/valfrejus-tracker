import os
from playwright.sync_api import sync_playwright
from PIL import Image

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # On simule un écran plus grand pour être sûr que la carte s'affiche bien
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # URL officielle du plan interactif
        url = "https://www.valfrejus.com/plan-des-pistes/" 
        
        try:
            print(f"Connexion à {url}...")
            # On attend que la page soit chargée
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # On attend un peu plus pour que les scripts de la carte s'activent
            print("Attente du rendu de la carte...")
            page.wait_for_timeout(15000) 

            # On prend la capture d'écran
            screenshot_path = "check.png"
            page.screenshot(path=screenshot_path, full_page=False)

            # Analyse du pixel (534, 905)
            img = Image.open(screenshot_path)
            # On vérifie si l'image est assez grande
            width, height = img.size
            print(f"Capture réussie : {width}x{height}")

            # On récupère la couleur
            pixel = img.getpixel((534, 905)) 
            r, g, b = pixel[0], pixel[1], pixel[2]
            print(f"Couleur détectée à (534,905) -> R:{r} G:{g} B:{b}")

            # Logique : Vert dominant = OPEN, sinon CLOSED
            # (Le vert de Skiplan est environ R:30, G:180, B:30)
            if g > r + 40 and g > 100:
                status = "OPEN"
            else:
                status = "CLOSED"
            
        except Exception as e:
            print(f"Erreur lors du scan : {e}")
            status = "ERROR"

        # On écrit le résultat
        with open("status.txt", "w") as f:
            f.write(status)
        print(f"Résultat sauvegardé : {status}")

        browser.close()

if __name__ == "__main__":
    run()

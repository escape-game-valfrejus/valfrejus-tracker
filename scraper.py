import os
from playwright.sync_api import sync_playwright
from PIL import Image

def run():
    with sync_playwright() as p:
        # 1. On lance un navigateur identique à un humain
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 2. On charge la page (on utilise l'URL du widget directement pour être plus léger)
        url = "https://live.skitrak.com/valfrejus/" 
        print(f"Chargement de {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 3. On attend que les pastilles de couleur apparaissent (important !)
        page.wait_for_timeout(10000) 

        # 4. On prend une photo de la zone précise (Asset 1991)
        # On définit une petite zone autour de X=534, Y=905 pour l'analyse
        screenshot_path = "check.png"
        page.screenshot(path=screenshot_path)

        # 5. Analyse de la couleur du pixel
        img = Image.open(screenshot_path)
        # On vérifie la couleur au point exact (ajustement possible selon le rendu)
        pixel = img.getpixel((534, 905)) 
        r, g, b = pixel[0], pixel[1], pixel[2]

        # Logique simplifiée : si le Vert est dominant -> OPEN
        status = "OPEN" if g > r and g > 150 else "CLOSED"
        
        print(f"Couleur détectée (RGB): {r},{g},{b} -> Statut: {status}")

        # 6. Sauvegarde du résultat dans un fichier texte
        with open("status.txt", "w") as f:
            f.write(status)

        browser.close()

if __name__ == "__main__":
    run()

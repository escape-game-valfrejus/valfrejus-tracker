import os
from playwright.sync_api import sync_playwright
from PIL import Image

def get_color_status(img, x, y):
    # On regarde une petite zone de 5x5 pixels pour être plus fiable
    r_total, g_total, b_total = 0, 0, 0
    count = 0
    for i in range(x-2, x+3):
        for j in range(y-2, y+3):
            r, g, b = img.getpixel((i, j))
            r_total += r
            g_total += g
            b_total += b
            count += 1
    
    avg_r, avg_g, avg_b = r_total/count, g_total/count, b_total/count
    print(f"Zone ({x},{y}) -> R:{avg_r:.1f} G:{avg_g:.1f} B:{avg_b:.1f}")
    
    # Logique Skiplan : Le vert est très vif (G > 150), le rouge est (R > 150)
    if avg_g > avg_r + 30 and avg_g > 100:
        return "1" # OUVERT
    else:
        return "0" # FERMÉ (ou Orange/Attente)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1500})
        page = context.new_page()

        url = "https://valfrejus.digisnow.app/map/1/fr?fullscreen=true"
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000) # On laisse le temps aux pastilles d'apparaître
            
            screenshot_path = "debug_map.png"
            page.screenshot(path=screenshot_path)
            img = Image.open(screenshot_path)

            # Utilisation de tes coordonnées précises
            # TCD Arrondaz : X 255, Y 1088
            status_arrondaz = get_color_status(img, 255, 1088)
            
            # TSD Punta Bagna : X 827, Y 480
            status_punta = get_color_status(img, 827, 480)

            # Ecriture du fichier pour l'ESP32
            # Format : A:1,P:1 (A=Arrondaz, P=Punta)
            result = f"A:{status_arrondaz},P:{status_punta}"
            with open("status.txt", "w") as f:
                f.write(result)
            
            print(f"Fichier status.txt mis à jour : {result}")

        except Exception as e:
            print(f"Erreur : {e}")
            with open("status.txt", "w") as f:
                f.write("A:0,P:0")

        browser.close()

if __name__ == "__main__":
    run()

import os
import time
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright
from PIL import Image

# Fonction pour analyser la couleur et retourner la lettre pour l'ESP32
def get_color_status(img, x, y):
    r, g, b = img.getpixel((x, y))
    print(f"Analyse point ({x},{y}) -> R:{r} G:{g} B:{b}")
    
    # VERT (Ouvert) -> On envoie V
    if g > r + 30 and g > 100: 
        return "V"
    # ORANGE (En attente) -> On envoie B pour tes LEDs BLEUES
    elif r > 180 and g > 120 and b < 100: 
        return "B"
    # ROUGE (Fermé) -> On envoie R
    else:
        return "R"

# Fonction de vérification Calendrier et Heure
def is_season_and_time():
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    
    # 1. Vérification Dates (15 Décembre au 20 Avril)
    month = now.month
    day = now.day
    # En saison si (Décembre et jour >= 15) OU (Janvier à Mars) OU (Avril et jour <= 20)
    in_season = (month == 12 and day >= 15) or (1 <= month <= 3) or (month == 4 and day <= 20)
    
    if not in_season:
        print("Hors saison (15 dec - 20 avril).")
        return False
        
    # 2. Vérification Heures (08:40 à 16:30)
    current_time = now.strftime("%H:%M")
    if not ("08:40" <= current_time <= "16:30"):
        print(f"Hors créneau horaire ({current_time}).")
        return False
        
    return True

def run_loop():
    print("Démarrage du script de surveillance...")
    
    with sync_playwright() as p:
        # Configuration du navigateur
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1500})
        page = context.new_page()
        url = "https://valfrejus.digisnow.app/map/1/fr?fullscreen=true"

        # Boucle interne de 14 minutes (pour rester sous la limite GitHub de 15min)
        start_script_time = time.time()
        while (time.time() - start_script_time) < 840: 
            
            if is_season_and_time():
                try:
                    print(f"\n--- Scan de {datetime.now().strftime('%H:%M:%S')} ---")
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(10000) # Attente chargement pastilles
                    
                    screenshot_path = "debug_map.png"
                    page.screenshot(path=screenshot_path)
                    img = Image.open(screenshot_path)

                    # Analyse avec TES coordonnées précises
                    # TCD Arrondaz (X:255, Y:1088)
                    s_arr = get_color_status(img, 255, 1088)
                    # TSD Punta Bagna (X:827, Y:480)
                    s_pun = get_color_status(img, 827, 480)

                    # Formatage du résultat pour l'ESP32
                    result = f"A:{s_arr},P:{s_pun}"
                    
                    # Sauvegarde locale
                    with open("status.txt", "w") as f:
                        f.write(result)
                    
                    # Envoi vers GitHub (Push)
                    os.system('git config --global user.name "SkiBot"')
                    os.system('git config --global user.email "bot@github.com"')
                    os.system('git add status.txt')
                    # On commit seulement s'il y a un changement pour ne pas saturer l'historique
                    os.system('git commit -m "Update status" || echo "Pas de changement"')
                    os.system('git push')
                    
                    print(f"Statut envoyé : {result}")

                except Exception as e:
                    print(f"Erreur pendant le scan : {e}")
            else:
                # Si hors créneau, on crée un fichier "Fermé" par sécurité
                with open("status.txt", "w") as f:
                    f.write("A:R,P:R")
            
            # Pause de 30 secondes
            time.sleep(30)

        browser.close()

if __name__ == "__main__":
    run_loop()

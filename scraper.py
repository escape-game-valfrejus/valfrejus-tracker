import time
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright
from PIL import Image

def get_color_status(img, x, y):
    r, g, b = img.getpixel((x, y))
    # Logique des 3 couleurs
    if g > r + 40 and g > 100: return "V"  # VERT (Ouvert)
    if r > g + 40 and r > 100: return "R"  # ROUGE (Fermé)
    if r > 150 and g > 100 and b < 100: return "B" # ORANGE -> BLEU (Pending)
    return "R" # Par défaut Fermé

def is_season_and_time():
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    
    # Vérification Dates (15 Dec au 20 Avril)
    month_day = (now.month, now.day)
    if not ((month_day >= (12, 15)) or (month_day <= (4, 20))):
        return False
        
    # Vérification Heures (08:40 à 16:30)
    current_time = now.strftime("%H:%M")
    if not ("08:40" <= current_time <= 16:30"):
        return False
        
    return True

def run_loop():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1500})
        page = context.new_page()
        
        # On fait tourner le script pendant 14 minutes (pour éviter le timeout GitHub de 15min)
        start_time = time.time()
        while (time.time() - start_time) < 840: 
            if is_season_and_time():
                try:
                    page.goto("https://valfrejus.digisnow.app/map/1/fr?fullscreen=true", wait_until="networkidle")
                    page.wait_for_timeout(5000)
                    
                    screenshot_path = "debug_map.png"
                    page.screenshot(path=screenshot_path)
                    img = Image.open(screenshot_path)

                    # Tes coordonnées
                    s_arr = get_color_status(img, 255, 1088) # Arrondaz
                    s_pun = get_color_status(img, 827, 480)  # Punta Bagna

                    result = f"A:{s_arr},P:{s_pun}"
                    with open("status.txt", "w") as f:
                        f.write(result)
                    
                    # Committer le fichier via ligne de commande pour mise à jour réelle
                    os.system('git config --global user.name "SkiBot"')
                    os.system('git config --global user.email "bot@github.com"')
                    os.system('git add status.txt && git commit -m "Update" && git push || echo "No change"')
                    
                except Exception as e:
                    print(f"Erreur: {e}")
            
            time.sleep(30) # Pause de 30 secondes avant le prochain scan
        browser.close()

if __name__ == "__main__":
    run_loop()

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
URUN_LISTESI = [
    "https://www.bershka.com/tr/f%C4%B1r%C3%A7alanm%C4%B1%C5%9F-efektli-desenli-s%C3%BCveter-c0p200314447.html?colorId=800",
    "https://www.bershka.com/tr/teknik-spor-ceket-c0p189277209.html?colorId=401",
    "https://www.bershka.com/tr/vinil-efektli-suni-k%C3%BCrkl%C3%BC-yaka-ceket-c0p197723477.html?colorId=800"
]

HEDEF_BEDEN = "M"
# DİKKAT: Tokenin buradaki mesajda göründüğü için internete düştü. 
# Güvenlik için BotFather'dan yeni token almanı öneririm. Şimdilik seninkileri koydum:
TELEGRAM_TOKEN = "8495759843:AAHsFKuoITm87HdEBUEkAC8QiudWFWlddnc"
CHAT_ID = "1564732604"

def send_telegram_message(message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(f"Mesaj hatası: {e}")

def toplu_kontrol():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = None
    stok_bulunanlar = []

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        for link in URUN_LISTESI:
            print(f"[{time.strftime('%H:%M:%S')}] Kontrol: {link[-20:]}...") 
            try:
                driver.get(link)
                
                # --- AKILLI BEKLEME VE SCROLL ---
                time.sleep(2) # İlk yükleme
                driver.execute_script("window.scrollTo(0, 500);") # Tetikleme
                time.sleep(4) # Veri gelmesi için bekleme
                # --------------------------------

                xpath_sorgusu = f"//span[normalize-space()='{HEDEF_BEDEN}'] | //button[normalize-space()='{HEDEF_BEDEN}']"
                olasi_bedenler = driver.find_elements(By.XPATH, xpath_sorgusu)
                
                found_in_link = False
                
                for element in olasi_bedenler:
                    try:
                        if not element.is_displayed(): continue

                        parent = element.find_element(By.XPATH, "./..")
                        grandparent = parent.find_element(By.XPATH, "./..")
                        
                        classes = (element.get_attribute("class") or "") + " " + \
                                  (parent.get_attribute("class") or "") + " " + \
                                  (grandparent.get_attribute("class") or "")
                        classes = classes.lower()
                        
                        aria_disabled = element.get_attribute("aria-disabled")
                        parent_aria = parent.get_attribute("aria-disabled")

                        # --- DETAYLI FİLTRE ---
                        if "disabled" in classes or "no-stock" in classes: continue
                        if aria_disabled == "true" or parent_aria == "true": continue
                        if "guide" in classes or "ruler" in classes: continue
                        
                        found_in_link = True
                        print(f"   -> STOK BULUNDU! ({link})")
                        break 
                    except: continue
                
                if found_in_link:
                    msg = f"🚨 MÜJDE! {HEDEF_BEDEN} beden stokta!\nLink: {link}"
                    send_telegram_message(msg)
                    stok_bulunanlar.append(link)
                else:
                    print(f"   -> Stok Yok.")
                
                time.sleep(2)

            except Exception as e:
                print(f"   -> Hata: {e}")
                continue

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        if driver: driver.quit()

# --- BURASI DEĞİŞTİ: WHILE LOOP YOK, TEK SEFER ÇALIŞIR ---
if __name__ == "__main__":
    toplu_kontrol()
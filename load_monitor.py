from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import paho.mqtt.publish as publish
import time

# Konfiguration
url = "http://192.168.X.X/"   # Inverter IP
password = "PASSWORD"         # Password for your Inverter
mqtt_broker = "192.168.X.X"   # MQTT broker IP
mqtt_port = 1883
mqtt_user = "youruser"
mqtt_pass = "yourpassword"
mqtt_topic_base = "load/status"
polling_interval = 60 # seconds
# max_laufzeit = 60 * 60  # z. B. 1 Stunde (optional beenden nach 1h)

# Browser vorbereiten
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

try:
    driver.get(url)

    # Loginmaske öffnen
    login_div = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.menu-button-container"))
    )
    login_div.click()
    time.sleep(1.5)

    # Passwortfeld ausfüllen & Login
    pass_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mat-input-0"))
    )
    pass_input.send_keys(password)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fro-button-primary"))
    )
    login_button.click()
    time.sleep(3)

    # Lastmanagement-Seite öffnen
    driver.get("http://192.168.X.X/#/load-management") # fill in your inverter IP
    time.sleep(5)

    # Letzter Status zum Vergleich
    last_state = ["", "", "", ""]

    starttime = time.time()

    while True:
        punkte = driver.find_elements(By.CSS_SELECTOR, ".status")[:4]
        status_liste = []

        for punkt in punkte:
            klasse = punkt.get_attribute("class")
            if "success" in klasse:
                status_liste.append("on")
            elif "failure" in klasse:
                status_liste.append("off")
            else:
                status_liste.append(f"unknown")

        # Nur senden wenn sich etwas geändert hat
        if status_liste != last_state:
            print("state changed:", status_liste)
            last_state = status_liste.copy()

            messages = []
            for i, s in enumerate(status_liste, start=1):
                topic = f"{mqtt_topic_base}/phase{i}"
                messages.append((topic, s, 0, False))

            publish.multiple(messages,
                             hostname=mqtt_broker,
                             port=mqtt_port,
                             auth={'username': mqtt_user, 'password': mqtt_pass})

        else:
            print("no change:", status_liste)

# Zeitstempel für letzte erfolgreiche Aktualisierung
        timestamp = datetime.now().isoformat()

        publish.single("load/status/last_update",
                       timestamp,
                       hostname=mqtt_broker,
                       port=mqtt_port,
                       auth={'username': mqtt_user, 'password': mqtt_pass})

        print(f"last update sent: {timestamp}")

        time.sleep(polling_interval)

        # Optional nach Zeit abbrechen
#        if time.time() - startzeit > max_laufzeit:
#            print("Maximale Laufzeit erreicht – beende Skript.")
#            break

except Exception as e:
    print("❌ Failure:", e)
    driver.save_screenshot("debug_error.png")

finally:
    driver.quit()
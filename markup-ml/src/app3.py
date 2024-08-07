from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.binary_location = '/snap/chromium/2873/usr/lib/chromium-browser/chrome'  # Ruta al navegador Chromium
chrome_service = Service('/snap/chromium/2873/usr/lib/chromium-browser/chromedriver')  # Reemplaza con la ruta a tu ChromeDriver

# Inicializa el navegador
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Función para obtener las URLs de todas las páginas de resultados de Google hasta que no haya más
def get_all_google_search_urls(query):
    base_url = 'https://www.google.com'
    driver.get(base_url)
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # Espera para que se carguen los resultados

    urls = []
    while True:
        search_results = driver.find_elements(By.CSS_SELECTOR, 'div.yuRUbf > a')
        urls.extend([result.get_attribute('href') for result in search_results])
        
        # try:
        #     more_results_button = driver.find_element(By.CSS_SELECTOR, 'input[value="Más resultados"]')
        #     more_results_button.click()
        #     time.sleep(2)  # Espera para que se cargue la siguiente página
        # except NoSuchElementException:
        #     print('No more pages or blocked by Google.')
        #     break

    return urls

# Ejemplo de uso: obtener URLs de todas las páginas de resultados de Google
search_query = 'python web scraping'
urls = get_all_google_search_urls(search_query)
for url in urls:
    print(url)

# Cierra el navegador una vez finalizado
driver.quit()
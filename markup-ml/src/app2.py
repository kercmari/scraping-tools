from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from transformers import MarkupLMProcessor
import requests


# Configurar Selenium para usar Chromium
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Ejecuta en modo headless, sin abrir la ventana del navegador
chrome_options.binary_location = '/snap/chromium/2873/usr/lib/chromium-browser/chrome'  # Ruta al navegador Chromium
chrome_service = Service('/snap/chromium/2873/usr/lib/chromium-browser/chromedriver')  # Reemplaza con la ruta a tu ChromeDriver

# Inicializar el navegador
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Realizar una búsqueda en Google
query = "plantillas de marketing"
driver.get(f"https://www.google.com/search?q={query}")

# Esperar un momento para cargar los resultados
time.sleep(2)

# Obtener todas las URLs de las páginas de resultados
urls = []
for page_number in range(1, 6):  # Cambiar el rango según la cantidad de páginas que quieras obtener
    # Obtener el HTML de la página actual
    html = driver.page_source

    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Encontrar los resultados de búsqueda
    results = soup.find_all('div', class_='g')
    for result in results:
        link = result.find('a', href=True)
        if link:
            urls.append(link['href'])

    # Ir a la siguiente página de resultados
    # next_page_link = driver.find_element(By.XPATH, f'//a[@aria-label="Page {page_number + 1}"]')
    # next_page_link.click()

    # Esperar un momento para cargar la siguiente página
    time.sleep(2)

# Cerrar el navegador
driver.quit()

# Guardar las URLs en un archivo
with open("urls.txt", "w") as file:
    for url in urls:
        file.write(url + "\n")

# Leer las URLs del archivo
with open("urls.txt", "r") as file:
    urls_from_file = [line.strip() for line in file.readlines()]


# Cargar MarkupLMProcessor desde Hugging Face
processor = MarkupLMProcessor.from_pretrained("microsoft/markuplm-base")
# print ( 'urls_from_file', urls_from_file)
# Procesar cada URL
relevant_urls = []

for url in urls_from_file:
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Truncar el HTML en segmentos si es demasiado largo
        max_length = 512
        segments = [html_content[i:i+max_length] for i in range(0, len(html_content), max_length)]
    

        # Procesar cada segmento con MarkupLMProcessor
        for segment in segments:
            print('Este es el segmento',segment)
            encoding = processor(segment, return_tensors="pt")
            content_tokens = processor.tokenizer.convert_ids_to_tokens(encoding['input_ids'][0])

            # Verificar si las keywords están presentes en el contenido procesado
            if any(keyword in content_tokens for keyword in ["plantilla", "marketing", "diseño"]):
                relevant_urls.append(url)
                break  # Si alguna parte es relevante, no es necesario seguir procesando los segmentos


    except Exception as e:
        print(f"Error al procesar {url}: {e}")

print('Terminando el proceso ')
# Imprimir las URLs relevantes
for url in relevant_urls:
    print(f"Relevant URL: {url}")

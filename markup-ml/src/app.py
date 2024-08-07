from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Configura Selenium para usar Chromium
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Ejecuta en modo headless, sin abrir la ventana del navegador
chrome_options.binary_location = '/snap/chromium/2873/usr/lib/chromium-browser/chrome'  # Ruta al navegador Chromium
chrome_service = Service('/snap/chromium/2873/usr/lib/chromium-browser/chromedriver')  # Reemplaza con la ruta a tu ChromeDriver

# Inicializa el navegador
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Realiza una búsqueda en Google
query = "plantillas de marketing"
driver.get(f"https://www.google.com/search?q={query}")

# Espera un momento para cargar los resultados
time.sleep(2)

# Obtén el HTML de la página
html = driver.page_source

# Parsear el HTML con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Encuentra los resultados de búsqueda
results = soup.find_all('div', class_='g')
urls = []

for result in results:
    link = result.find('a', href=True)
    if link:
        urls.append(link['href'])

# Cierra el navegador
driver.quit()

# Imprimir las URLs
for url in urls:
    print(url)


# Cargar MarkupLM desde Hugging Face
tokenizer = AutoTokenizer.from_pretrained("microsoft/markuplm-base")
model = AutoModelForTokenClassification.from_pretrained("microsoft/markuplm-base")

def process_html(html):
    # Tokenizar el texto HTML
    inputs = tokenizer(html, return_tensors="pt", truncation=True, padding=True)

    # Obtener las predicciones del modelo
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1)

    # Procesar las predicciones (esto es un ejemplo básico y puede variar según el uso específico)
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    predicted_tokens = [tokens[i] for i in predictions[0]]

    return predicted_tokens

# Procesar cada URL
relevant_urls = []

for url in urls:
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        #print('conteniod de html',html_content)
        # Procesar el HTML con MarkupLM
        processed_content = process_html(html_content)

        # Aquí puedes agregar lógica adicional para verificar la relevancia de la página
        if any(keyword in processed_content for keyword in ["plantilla", "marketing", "diseño"]):
                relevant_urls.append(url)

    except Exception as e:
        print("")
        #print(f"Error procesando {url}: {e}")

# Imprimir las URLs relevantes
for url in relevant_urls:
    print(f"Relevant URL: {url}")

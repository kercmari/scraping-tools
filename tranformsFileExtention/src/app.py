import json
from deep_translator import GoogleTranslator
import datetime
import json
import os
import pandas as pd
import re
# Ejemplo de JSON


# Convertir JSON a diccionario de Python


# Lista de propiedades a excluir


# Lista de tipos de datos a excluir


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

# Función para eliminar emojis de un texto
def remove_emojis(text):
    if isinstance(text, str):
        # Expresión regular para eliminar emojis
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U0001F300-\U0001F5FF"  # Símbolos y pictogramas misceláneos
            u"\U0001F680-\U0001F6FF"  # Transporte y símbolos de mapa
            u"\U0001F1E0-\U0001F1FF"  # Banderas
            u"\U00002500-\U00002BEF"  # Dibujos de caja / geométricos
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010FFFF"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # Símbolos de variantes
            u"\u3030"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    return text

current_dir = os.path.dirname(os.path.abspath(__file__))
data= []
config_path = os.path.join(current_dir,"config.json")
# Leer el archivo JSON
with open(config_path, "r") as file:
    data = json.load(file)
if isinstance(data, list) and len(data) > 0:
    # Iterar sobre cada elemento de la lista
    for item in data:
        json_data= []
          
      
        update_data_path = item.get("update_data_path")
  

        
        # Construir la ruta al archivo plt.json dentro de la carpeta 'files'
        update_data_path_new = os.path.join(current_dir, "files", update_data_path)

        with open(update_data_path_new, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

       
        try:
            # Aplanar cada diccionario en la lista de JSON
            flattened_data = [flatten_dict(item) for item in json_data]
            # Crear un DataFrame con los datos aplanados
            df = pd.DataFrame(flattened_data)
            print("Row count is:", df.shape[0])
            # Imprimir el JSON resultante
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            new_name= update_data_path.split(".")[0]
            
            output_path = os.path.join(current_dir, "output",f"{new_name}_{timestamp}.csv")
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"Datos guardados correctamente en '{output_path}'")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

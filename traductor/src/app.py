import json
from deep_translator import GoogleTranslator
import datetime
import json
import os
# Ejemplo de JSON


# Convertir JSON a diccionario de Python


# Lista de propiedades a excluir


# Lista de tipos de datos a excluir


# Función para verificar si una clave completa está en la lista de exclusión
def is_excluded_key(key, exclude):
    return any(key.endswith(ex) for ex in exclude)

# Función para verificar si un tipo de dato está en la lista de exclusión
def is_excluded_type(value, exclude_types):
    type_name = type(value).__name__
    return type_name.lower() in exclude_types

# Función para traducir el JSON
def translate_json(data, src_lang, dest_lang, exclude_keys=[], exclude_types=[]):
    translator = GoogleTranslator(source=src_lang, target=dest_lang)
    
    def recursive_translate(d, parent_key=''):
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                if not is_excluded_key(full_key, exclude_keys) and not is_excluded_type(v, exclude_types):
                    if isinstance(v, (dict, list)):
                        recursive_translate(v, full_key)
                    else:
                        if isinstance(v, str):
                            d[k] = translator.translate(v)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                full_key = f"{parent_key}[{i}]"
                if not is_excluded_key(full_key, exclude_keys) and not is_excluded_type(item, exclude_types):
                    if isinstance(item, (dict, list)):
                        recursive_translate(item, full_key)
                    else:
                        if isinstance(item, str):
                            d[i] = translator.translate(item)
    recursive_translate(data)
    return data

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
        src_language = item.get("src_language")
        dest_language = item.get("dest_language")
        exclude_properties = item.get("exclude_properties")
        exclude_types = item.get("exclude_types")    
      
        update_data_path = item.get("update_data_path")
  

        
        # Construir la ruta al archivo plt.json dentro de la carpeta 'files'
        update_data_path_new = os.path.join(current_dir, "files", update_data_path)

        with open(update_data_path_new, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

       
        try:
            # Traducir los valores en el JSON
            translated_json_data = translate_json(json_data, src_language, dest_language, exclude_properties, exclude_types)

            # Convertir el diccionario a una cadena JSON
            json_output = json.dumps(translated_json_data, indent=4)

            # Imprimir el JSON resultante
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            new_name= update_data_path.split(".")[0]
            
            output_path = os.path.join(current_dir, "output",f"{new_name}_{timestamp}.json")
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_output)

        except Exception as e:
            print(f"Ocurrió un error: {e}")

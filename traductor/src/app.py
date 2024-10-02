import json
from deep_translator import GoogleTranslator, LibreTranslator
import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

# Función para verificar si una clave completa está en la lista de exclusión
def is_excluded_key(key, exclude):
    return any(key.endswith(ex) for ex in exclude)

# Función para verificar si un tipo de dato está en la lista de exclusión
def is_excluded_type(value, exclude_types):
    type_name = type(value).__name__
    return type_name.lower() in exclude_types

# Función para traducir un lote de textos utilizando Google Translate o LibreTranslate como respaldo
def translate_batch(texts, src_lang, dest_lang, max_retries=5, backoff_factor=2):
    translator = GoogleTranslator(source=src_lang, target=dest_lang)
    for attempt in range(max_retries):
        try:
            translations = translator.translate_batch(texts)
            return translations
        except Exception as e:
            wait_time = backoff_factor ** attempt
            print(f"Error con Google Translate: {e}. Reintentando en {wait_time} segundos.")
            sleep(wait_time)
    
    # Si Google Translate falla, intentar con LibreTranslate
    print("Máximo número de intentos alcanzado con Google Translate. Cambiando a LibreTranslate...")
    libre_translator = LibreTranslator(source=src_lang, target=dest_lang)
    for attempt in range(max_retries):
        try:
            translations = [libre_translator.translate(text) for text in texts]
            return translations
        except Exception as e:
            wait_time = backoff_factor ** attempt
            print(f"Error con LibreTranslate: {e}. Reintentando en {wait_time} segundos.")
            sleep(wait_time)
    
    raise Exception("Máximo número de intentos alcanzado para la traducción del lote con ambos servicios.")

# Función para procesar un lote de traducciones en paralelo
def process_batch(batch, src_lang, dest_lang, exclude_keys, exclude_types, max_retries=5, backoff_factor=2):
    texts_to_translate = []
    keys_to_translate = []
    translated_keys = []

    def recursive_collect(d, parent_key=''):
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, str) and not is_excluded_key(full_key, exclude_keys) and not is_excluded_type(v, exclude_types):
                    texts_to_translate.append(v)
                    keys_to_translate.append((d, k))
                    translated_keys.append(full_key)
                elif isinstance(v, (dict, list)):
                    recursive_collect(v, full_key)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                full_key = f"{parent_key}[{i}]"
                if isinstance(item, str) and not is_excluded_key(full_key, exclude_keys) and not is_excluded_type(item, exclude_types):
                    texts_to_translate.append(item)
                    keys_to_translate.append((d, i))
                    translated_keys.append(full_key)
                elif isinstance(item, (dict, list)):
                    recursive_collect(item, full_key)

    for item in batch:
        recursive_collect(item)

    if texts_to_translate:
        translations = translate_batch(texts_to_translate, src_lang, dest_lang, max_retries, backoff_factor)
        for (obj, key), translation in zip(keys_to_translate, translations):
            obj[key] = translation

    return batch, translated_keys

# Función principal para traducir el JSON en paralelo
def translate_json_parallel(data, src_lang, dest_lang, exclude_keys=[], exclude_types=[], batch_size=100, request_delay=1, retry_delay=5, max_retries=5, backoff_factor=2):
    translated_data = []
    all_translated_keys = []
    total_batches = (len(data) + batch_size - 1) // batch_size  # Calcular el número total de lotes
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            future = executor.submit(process_batch, batch, src_lang, dest_lang, exclude_keys, exclude_types, max_retries, backoff_factor)
            futures.append(future)
            print(f"Enviando lote {i//batch_size + 1} de {total_batches} para traducción...")
            sleep(request_delay)

        for i, future in enumerate(as_completed(futures), 1):
            try:
                batch_data, batch_translated_keys = future.result()
                translated_data.extend(batch_data)
                all_translated_keys.extend(batch_translated_keys)
                percentage_completed = (i / total_batches) * 100
                print(f"Lote {i} de {total_batches} completado. Progreso: {percentage_completed:.2f}%")
            except Exception as e:
                print(f"Error al procesar el lote {i}: {e}. Esperando {retry_delay} segundos antes de reintentar...")
                sleep(retry_delay)

    return translated_data, all_translated_keys

# Ruta actual del directorio
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.json")

# Leer el archivo JSON de configuración
with open(config_path, "r") as file:
    data = json.load(file)

if isinstance(data, list) and len(data) > 0:
    for item in data:
        src_language = item.get("src_language")
        dest_language = item.get("dest_language")
        exclude_properties = item.get("exclude_properties")
        exclude_types = item.get("exclude_types")
        update_data_path = item.get("update_data_path")
        batch_size = item.get("batch_size", 100)
        request_delay = item.get("request_delay", 1)
        retry_delay = item.get("retry_delay", 5)
        
        update_data_path_new = os.path.join(current_dir, "files", update_data_path)

        with open(update_data_path_new, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        try:
            print(f"Traduciendo archivo: {update_data_path}")
            translated_json_data, translated_keys = translate_json_parallel(
                json_data, src_language, dest_language, exclude_properties, exclude_types,
                batch_size=batch_size, request_delay=request_delay, retry_delay=retry_delay)

            json_output = json.dumps(translated_json_data, indent=4)

            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            new_name = update_data_path.split(".")[0]
            
            output_path = os.path.join(current_dir, "output", f"{new_name}_{timestamp}.json")
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_output)

            translated_keys_path = os.path.join(current_dir, "output", f"{new_name}_translated_keys_{timestamp}.txt")
            with open(translated_keys_path, 'w', encoding='utf-8') as log_file:
                log_file.write("\n".join(translated_keys))
            
            print(f"Traducción completada para: {update_data_path}")
            print(f"Archivo traducido guardado en: {output_path}")
            print(f"Claves traducidas guardadas en: {translated_keys_path}")

        except Exception as e:
            print(f"Ocurrió un error al traducir {update_data_path}: {e}")

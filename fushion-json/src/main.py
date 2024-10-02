import os
import json
from datetime import datetime

# Función para leer el archivo de configuración
def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

# Función para leer y fusionar todos los archivos JSON en una carpeta
def merge_json_files(folder_path):
    merged_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                if isinstance(data, list):  # Asegúrate de que cada archivo contiene una lista
                    merged_data.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a list, skipping...")
    
    return merged_data

# Función para guardar el archivo JSON fusionado con una marca de tiempo
def save_merged_json(output_folder, merged_data):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"merged_output_{timestamp}.json"
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, 'w') as output_file:
        json.dump(merged_data, output_file, indent=4)
    
    print(f"Archivo fusionado guardado en: {output_path}")

def main():
    # Ruta del archivo de configuración
    config_path = os.path.join('..', 'config', 'config.json')
    
    # Cargar la configuración
    config = load_config(config_path)

    # Rutas desde el archivo de configuración
    file_folder = config['fileFolder']
    output_folder = config['outputFolder']

    # Fusionar los archivos JSON
    merged_data = merge_json_files(file_folder)

    # Guardar el archivo fusionado
    save_merged_json(output_folder, merged_data)

if __name__ == "__main__":
    main()

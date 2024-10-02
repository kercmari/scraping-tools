import json
import os
import time
from configurator import Configurator

class FakerModule:
    def __init__(self, config):
        self.config = config
        self.configurator = Configurator(config)

    def generate_data(self):
        data_list = []
        total = self.config.get('total', 1)
        for _ in range(total):
            data = {}
            for field, field_config in self.config['properties'].items():
                generator = self.configurator.get_generator(field_config)
                data[field] = generator.generate(self.parse_config(field_config))
            data_list.append(data)
        return data_list

    def parse_config(self, field_config):
        config = {}
        parts = field_config.split()
        for part in parts[1:]:
            key, value = part.split('=')
            config[key] = float(value) if '.' in value else int(value)
        return config

def main():
    # Verificar que el archivo de configuración existe
    config_file = '../config/config.json'
    if not os.path.exists(config_file):
        print(f"Error: No se encuentra el archivo de configuración en {config_file}")
        return
    
    # Leer configuración desde el archivo JSON
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: El archivo de configuración no es un JSON válido: {e}")
        return
    
    # Inicializar y generar datos
    faker_module = FakerModule(config)
    data_list = faker_module.generate_data()
    
    # Crear el directorio 'output' si no existe
    output_dir = '../output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar nombre del archivo con timestamp UNIX
    timestamp = int(time.time())
    output_file = f"{output_dir}/{timestamp}.json"
    
    # Guardar los datos generados en un archivo JSON
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)
    
    print(f"Datos generados y guardados en {output_file}")

if __name__ == '__main__':
    main()

import json
import pandas as pd

# Ejemplo de lista de objetos JSON
data = '''
[
    {
        "name": "John",
        "age": 30,
        "cars": [
            {"model": "Ford", "mpg": 25.5},
            {"model": "BMW", "mpg": 29.5}
        ],
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zipcode": "10001"
        }
    },
    {
        "name": "Anna",
        "age": 22,
        "cars": [
            {"model": "Audi", "mpg": 28.5}
        ],
        "address": {
            "street": "456 Maple St",
            "city": "Los Angeles",
            "zipcode": "90001"
        }
    }
]
'''

# Convertir JSON a lista de diccionarios de Python
json_data = json.loads(data)

# Función para aplanar un diccionario anidado
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

# Aplanar cada diccionario en la lista de JSON
flattened_data = [flatten_dict(item) for item in json_data]

# Crear un DataFrame con los datos aplanados
df = pd.DataFrame(flattened_data)

# Especificar el nombre del archivo CSV de salida
csv_file_path = 'output.csv'

# Guardar el DataFrame en un archivo CSV
try:
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    print(f"Datos guardados correctamente en '{csv_file_path}'")
except Exception as e:
    print(f"Ocurrió un error: {e}")

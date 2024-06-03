import pandas as pd
import json
# Ejemplo de DataFrame con datos JSON
data = [
    {"nombre": "Juan", "edad": 30, "contacto": {"email": "juan@example.com", "telefono": "123456789", "direccion": {"calle": "Av. Principal", "ciudad": "Ciudad X", "codigo_postal": "12345"}}},
    {"nombre": "María", "edad": 25, "contacto": {"email": "maria@example.com", "telefono": "987654321", "direccion": {"calle": "Av. Secundaria", "ciudad": "Ciudad Y", "codigo_postal": "54321" , "test": {"codigo_postal": "54321" }}}}
]

# Convertir a DataFrame
df = pd.DataFrame(data)

# Función para buscar y actualizar la clave específica en una fila
def buscar_actualizar_fila(fila, clave_buscada, nuevo_valor):
    for key, value in fila.items():
        print(key)
        if key == clave_buscada:
            fila[key] = nuevo_valor
        elif isinstance(value, dict):
            buscar_actualizar_fila(value, clave_buscada, nuevo_valor)

# Clave a buscar y nuevo valor
clave_buscada = "codigo_postal"
nuevo_valor = "kerly"

# Recorrer cada fila del DataFrame
for index, row in df.iterrows():
    buscar_actualizar_fila(row, clave_buscada, nuevo_valor)

json_resultado = df.to_json(orient="records")

# Imprimir el JSON desnormalizado
print(json_resultado)
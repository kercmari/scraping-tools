import re
import pandas as pd
from fuzzywuzzy import process
import datetime
import json
import os
# Listado de data a actualizar

def list_to_dict(lst, key_prop, value_prop):
    """
    Convert a list of dictionaries to a dictionary using specified key and value properties.
    
    :param lst: List of dictionaries
    :param key_prop: The property to use as keys for the new dictionary
    :param value_prop: The property to use as values for the new dictionary
    :return: A dictionary with keys and values based on specified properties
    """
    result_dict = {}
 

    for i, item in lst.iterrows():
        
        key = str(item[key_prop]).lower()
        value = item[value_prop]
        result_dict[key] = value  
    return result_dict
# Convertimos la lista de data actualizar en un diccionario para acceso rápido

def search_and_update_row(row, key_propertie, new_value):
    for key in row.keys():
        if key_propertie in key:
            row[key] = new_value  # Actualizar el valor de la clave encontrada

def search_and_update_key(json_data, key_propertie, new_value):
    if isinstance(json_data, dict):  # Si es un diccionario
        for key, value in json_data.items():
            if key == key_propertie:
                json_data[key] = new_value  # Actualizar el valor de la clave
            else:
                search_and_update_key(value, key_propertie, new_value)  # Llamada recursiva para buscar en el valor
    elif isinstance(json_data, list):  # Si es una lista
        for item in json_data:
            search_and_update_key(item, key_propertie, new_value) 

# Función para actualizar la data
def search_and_update_df(data_df, key_propertie, new_value):
    for column in data_df.columns:
        if key_propertie in column:
            data_df[column] = new_value  # Actualizar el valor de la clave encontrada

def search_and_update_property(data, property_name, new_value):
    
    if isinstance(data, dict):  # Si es un diccionario
        for key, value in data.items():
            if key == property_name:
                #print
          
                data[key] = new_value  # Actualizar el valor de la propiedad
            else:
                search_and_update_property(value, property_name, new_value)  # Llamada recursiva para buscar en el valor
    elif isinstance(data, list):  # Si es una lista
        for item in data:
            search_and_update_property(item, property_name, new_value)  # Llamada recursiva para buscar en cada elemento de la lista
def buscar_actualizar_fila(fila, clave_buscada, nuevo_valor):
    for key, value in fila.items():
      
        if key == clave_buscada:
            fila[key] = nuevo_valor
        elif isinstance(value, dict):
            buscar_actualizar_fila(value, clave_buscada, nuevo_valor)
        elif isinstance(value, list):
            for item in value:
                buscar_actualizar_fila(item, clave_buscada, nuevo_valor)
def update_plates_with_ingredient_ids(data_df, ingredient_dict, input_info, key_propertie_update,key_type, split_key= '-'):
    for i, data in data_df.iterrows():
        # Descomponer plt_info en una lista de palabras, separadas por espacio y/o coma
        if  data[input_info]:
            plt_info_ingredients = re.split(r',?\s+', data[input_info].lower())
            
            # Inicializar una lista para almacenar los nuevos IDs
            new_ingredient_ids = []
            
            # Verificar cada ingrediente en plt_info
            for ingredient in plt_info_ingredients:
                best_match, score = process.extractOne(ingredient, ingredient_dict.keys())
                if score >= 80:
                    new_ingredient_ids.append(ingredient_dict[best_match])
        
            # Actualizar plt_ingredients_id concatenando los nuevos IDs con un guion
            
            if new_ingredient_ids:
                new_input = new_ingredient_ids
                if (key_type == 'string'):
                    new_input= split_key.join( new_ingredient_ids)
               
                buscar_actualizar_fila(data, update_key, new_input)
               
                # print (data_df.at[i, update_key])
                #data_df.at[i, update_key] =new_input
    return data_df
#Solicitar los datos 
# Solicitar rutas de archivos y parámetros por consola
# update_data_path = input("Ingrese la ruta del archivo JSON de datos a actualizar o los datos base para analisis: ")
# data_ids_path = input("Ingrese la ruta del archivo JSON de IDs: ")
# key_prop = input("Ingrese la key property a comparar (por ejemplo, 'ing_name'): ").lower()
# value_prop = input("Ingrese la key property para obtener el ID (por ejemplo, 'objectId'): ").lower()
# info_key = input("Ingrese la key de la fuente de información (por ejemplo, 'plt_info'): ").lower()
# update_key = input("Ingrese la key para actualizar los nuevos IDs (por ejemplo, 'plt_ingredients_id'): ").lower()

# Obtener la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
data= []
config_path = os.path.join(current_dir,"config.json")
# Leer el archivo JSON
with open(config_path, "r") as file:
    data = json.load(file)
if isinstance(data, list) and len(data) > 0:
    # Iterar sobre cada elemento de la lista
    for item in data:
    
        key_prop = item.get("key_prop")
        key_type = item.get("key_type")
        value_prop = item.get("value_prop")
        info_key = item.get("info_key")
        update_key = item.get("update_key")
        split_key = item.get("split_key")
        update_data_path = item.get("update_data_path")
        data_ids_path = item.get("data_ids_path")
        # Construir la ruta al archivo plt.json dentro de la carpeta 'files'
        update_data_path_new = os.path.join(current_dir, "files", update_data_path)
        data_ids_path_new = os.path.join(current_dir, "files", data_ids_path)

        # Keys



        try:
            data_df = pd.read_json(update_data_path_new)
        except ValueError as e:
            print(f"Error al leer el archivo de datos a actualizar: {e}")
            exit(1)
        except FileNotFoundError as e:
            print(f"Archivo de datos a actualizar no encontrado: {e}")
            exit(1)

        try:
            ikeys_df = pd.read_json(data_ids_path_new)
        except ValueError as e:
            print(f"Error al leer el archivo de IDs: {e}")
            exit(1)
        except FileNotFoundError as e:
            print(f"Archivo de IDs no encontrado: {e}")
            exit(1)
        try:
            data_dict = list_to_dict(ikeys_df ,key_prop, value_prop)
        except Exception as e:
            print(f"Error de key porperties: {e}")
            exit(1)


        #print (data_dict)
        updated_data = update_plates_with_ingredient_ids(data_df, data_dict, info_key, update_key,key_type, split_key)



        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        new_name= update_data_path.split(".")[0]
        
        output_path = os.path.join(current_dir, "output",f"{new_name}_{timestamp}.json")
        updated_data.to_json(output_path, orient='records', indent=4)
        count_row= updated_data.shape[0]
        print(f"Los datos actualizados se han guardado en {output_path}, con esta cantidad de archivos {count_row}")

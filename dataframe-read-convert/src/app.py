import json
import os
import pandas as pd
import datetime
import random

# Define la estructura estándar de las propiedades del objeto


def estandarizar_dataframe(df, estructura, renombrar=None):
    # Renombra las columnas si es necesario
    if renombrar:        
        df = df.rename(columns=renombrar)
     
    #df = df.loc[:, ~df.columns.duplicated()]
    # Alinea el DataFrame a la estructura estándar
 
    df_estandarizado = df.reindex(columns=estructura)
    return df_estandarizado

def seleccionar_filas(df, num_filas):
    return df.head(num_filas) if num_filas else df
def generar_valor(col_values, type):
    valor = random.choice(col_values)
    if type=='string':
        valor = str(valor)
    return valor
def generar_valor_aleatorio(rango):
    valor = random.randint(rango[0], rango[1])
    return f'{valor}.00'
def multiplicar_por_factor(row, columnas, factor, type_data):
    val1 = row[columnas[0]]
    val2 = row[columnas[1]]
    resultado = float(val1) * float(val2) * factor
    resultado= round(resultado, 2)
    if type_data=='string':
        resultado = str(resultado)
    return resultado

def dividir_valor(row, columna,word_split ,value, type_data):
    #print('Prin de row',row)
    if row[columna]:
    #    print('+++++++++++++++++++=Este es el valor de la columna',row[columna])
        list_values = row[columna].split(word_split)
        value = list_values[value]

        resultado= value
        if type_data=='string':
            resultado = str(resultado)
        return resultado
def agregar_properties(df, properties_default):

    for prop in properties_default:
        col_name = prop['name']
        col_type = prop['type']
        col_factor =  prop.get('factor',None)
        col_list_column =  prop.get('list_column')
        col_function = prop.get('function', None)
        col_values = prop.get('values', [])
        col_default_value = prop.get('value', None)

        #Para Split
        column_name = prop.get('column_name', None)
        word_split = prop.get('word_split', None)

        if col_function == 'random' and col_values:
            df[col_name] = df.apply(lambda _: generar_valor(col_values, col_type), axis=1)
        elif col_function == 'random.range' and col_values:
            df[col_name] = df.apply(lambda _: generar_valor_aleatorio(col_values), axis=1)
        elif col_function == 'multiplication' :
        
            df[col_name] = df.apply(lambda row: multiplicar_por_factor(row, col_list_column, col_factor, col_type), axis=1)
        
        elif col_function == 'split':
            df[col_name] = df.apply(lambda row: dividir_valor(row, column_name,word_split, col_default_value, col_type), axis=1)
        
        else:
            df[col_name] = col_default_value if col_default_value is not None else ''
        
        # Cambiar el tipo de datos de la columna si es necesario
        if col_type == 'integer':
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce')

    return df
def type_data_function(df, properties_default):
 
    if properties_default:
        for prop in properties_default:
            col_name = prop['name']
            col_type = prop['type']
        
        
            # Cambiar el tipo de datos de la columna si es necesario
            if col_type == 'integer':
                df[col_name] = df[col_name].astype(int)
            elif col_type == 'float':
                df[col_name] = df[col_name].astype(float)
            else:
                df[col_name] =df[col_name].astype(str)
    return df

def leer_archivo(nombre_archivo):
    # Obtener la extensión del archivo
    _, extension = os.path.splitext(nombre_archivo.lower())

    # Leer el archivo según su extensión
    if extension == '.csv':
        data_df = pd.read_csv(nombre_archivo)
    elif extension == '.json':
        data_df = pd.read_json(nombre_archivo)
    elif extension == '.txt':
        # Asumiendo que el archivo TXT está delimitado por comas
        data_df = pd.read_csv(nombre_archivo, delimiter=',')
    else:
        raise ValueError(f"Extensión de archivo no compatible: {extension}")

    return data_df

def consolidar_y_exportar(lista_dfs, estructura, num_filas, renombrar,list_properties_default, list_type_data,nombre_archivo_json='archivo_consolidado.json'):
    dfs_estandarizados = []
    for df, filas, renom, properties_default,type_data in zip(lista_dfs, num_filas, renombrar,list_properties_default, list_type_data):
        df_add = agregar_properties(df, properties_default)
        df_estandarizado = estandarizar_dataframe(df_add, estructura, renom)     
        df_seleccionado = seleccionar_filas(df_estandarizado, filas)
        df_tipado = type_data_function(df_seleccionado, type_data)
        dfs_estandarizados.append(df_tipado)
    df_consolidado = pd.concat(dfs_estandarizados, ignore_index=True)
    # Exportar como una lista de objetos JSON
    json_str = df_consolidado.to_json(orient='records', indent=4)
    with open(nombre_archivo_json, 'w') as f:
        f.write(json_str)

current_dir = os.path.dirname(os.path.abspath(__file__))
data= []
config_path = os.path.join(current_dir,"config.json")
# Leer el archivo JSON
with open(config_path, "r") as file:
    data = json.load(file)

estructura_estandar = data.get("estructura_estandar")
dataframes = data.get("dataframes")
list_df = []
list_renombrar = []
list_count = []
list_type_data = []
list_properties_default = []
new_name = ''

if isinstance(dataframes, list) and len(dataframes) > 0:
    # Iterar sobre cada elemento de la lista
    
    for item in dataframes:
        rename = item.get("rename")
        count_row = item.get("count_row")
        data_path = item.get("data_path")
        type_data = item.get("type_data")
        properties_default = item.get("properties_default")

        path_new = os.path.join(current_dir, "files", data_path)       
     
        data_df = leer_archivo(path_new)

        # for propertie in properties_default:
        #     columna = propertie.get("name")
        #     valor_por_defecto = propertie.get("value")
        #     data_df[columna] = valor_por_defecto
        list_df.append(data_df)
        list_renombrar.append(rename)
        list_count.append(count_row)
        list_type_data.append(type_data)      
        list_properties_default.append(properties_default)

        #Obtener la ruta del archivo
        name_split= path_new.split(".")[0]
        division= name_split.split("/")[-1]
        new_name+= division.split(".")[0]

# Llamas a la función consolidar_y_exportar así:
now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d_%H%M%S")
nombre_archivo_json=f'{new_name}_{timestamp}.json'
path_out = os.path.join(current_dir, "output", nombre_archivo_json)   
print(f'El nombre del archivo generado es {path_new}')
consolidar_y_exportar(
    lista_dfs=list_df,
    estructura=estructura_estandar,
    num_filas=list_count,  # Número de filas que quieres de df1 y df2 respectivamente
    renombrar=list_renombrar,
    list_properties_default=list_properties_default,
    list_type_data=list_type_data,
    nombre_archivo_json= path_out
)
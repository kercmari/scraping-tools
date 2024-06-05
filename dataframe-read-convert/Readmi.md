## RUN ENV
```
python -m venv env
env\Scripts\activate
```

En caso de no tener permisos 

`Set-ExecutionPolicy RemoteSigned`

Instalar librerias 
`pip install -r requirements.txt `
Para compilar el codigo 
`python src/app.py`

## Documentation Config 

```json
 {
    "estructura_estandar": [
        "gender",
        "country"
    ], //Columnas finales del documento o tabla de interes
    
    "dataframes": [
        {
            "rename": {
                "name": "prodName",
                "actual_price": "prodPrice"
            }, // Objeto clave-valor, la clave es la columnas del documento actual, valor son las columnas que van a ser usadas en el documento final
            "type_data": [
                {
                "name": "prodPrice",
                "type": "string"
                },
                {
                    "name": "prodRating",
                    "type": "string"
                }
            ], //Lista de tipo de dato como se requiera el documento final
            "count_row": 20, //canitdad de elementos tomados del input file
            "data_path": "amazon.csv", //Nombre del input file
            "properties_default": [
                
                {
                    "name": "comName",
                    "type": "string",
                    "value": "Amazon"
                }, //esta configuracion se establece el nombre de la columna donde se define un valor por defecto para todas las rows, el key clave es "value"
                {
                    "name": "gender",
                    "type": "string",
                    "function": "random",
                    "values": [
                        "Male",
                        "Female"
            
                    ]
                }, //esta configuracion se establece el nombre de la columna donde se define un randon por defecto para todas las rows, el key clave es "function"   y    "values"  , donde values esta soportado para N elementos       
                {
                    "name": "offerPrice",
                    "type": "string",
                    "list_column": ["offerName", "prodPrice"],
                    "function": "multiplication",
                    "factor":0.01
                    
                }//esta configuracion se establece el nombre de la columna donde se define un una funcion operecion  por defecto para todas las rows, el key clave es "function" ,    "factor"  y "list_column" , list_column esta soportado para dos elemento 
            ] //Lista de properties generadas por defecto o ramdom
        }
    ]
}
    
```

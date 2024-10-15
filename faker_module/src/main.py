import json
import random
import shlex  # Importar shlex para dividir cadenas con comillas
from faker import Faker
from faker.config import AVAILABLE_LOCALES

# Cargar la colección base desde un archivo JSON
def load_base_collection(file_path):
    if not file_path:
        # Si file_path es una cadena vacía o None, retornar lista vacía
        return []
    else:
        with open(file_path, 'r') as f:
            return json.load(f)

class FakerModule:
    def __init__(self, config):
        self.config = config
        locale = config.get('locale', 'en_US') 
        if locale not in AVAILABLE_LOCALES:
            raise ValueError(f"Locale '{locale}' no es soportado por Faker.")
        self.faker = Faker(locale)  # Configurar Faker con el locale especificado

        # Manejar la colección base
        collection_path = config.get("collection", "")
        self.base_collection = load_base_collection(collection_path)

        self.properties_set = config['propertiesSet']
        self.properties_type_set = config['propertiesTypeSet']
        self.unique_values = {}      # Diccionario para almacenar listas de valores únicos pre-generados
        self.unique_indices = {}     # Diccionario para rastrear el índice actual en cada lista de valores únicos

        # Identificar y pre-generar valores únicos para campos configurados como únicos
        self.pre_generate_unique_values()

    def pre_generate_unique_values(self):
        """
        Identifica los campos únicos en la configuración y pre-genera sus valores únicos.
        """
        for parent_field, fields in self.properties_set.items():
            for field, field_config in fields.items():
                if isinstance(field_config, str):
                    config_parsed = self.parse_config(field_config)
                    if config_parsed.get('unique', False):
                        if config_parsed.get('type') != 'int':
                            raise ValueError(f"Actualmente, solo se soportan campos únicos de tipo 'int'. Campo '{field}' tiene tipo '{config_parsed.get('type')}'.")
                        min_val = config_parsed.get('min', 0)
                        max_val = config_parsed.get('max', 100)
                        total_unique = self.config.get('total', 1)

                        range_size = max_val - min_val + 1
                        if total_unique > range_size:
                            raise ValueError(f"El rango para el campo '{field}' ({min_val} a {max_val}) no es suficiente para generar {total_unique} valores únicos.")

                        print(f"Generando {total_unique} valores únicos para el campo '{field}' en el rango {min_val} a {max_val}.")
                        unique_ids = random.sample(range(min_val, max_val + 1), total_unique)
                        self.unique_values[field] = unique_ids
                        self.unique_indices[field] = 0

    def parse_min_max(self, field_config):
        # Extraer valores min y max de la configuración
        min_value = None
        max_value = None
        if isinstance(field_config, str):
            parts = field_config.split()
            for part in parts:
                if part.startswith('min='):
                    min_value = int(part.split('=', 1)[1])
                elif part.startswith('max='):
                    max_value = int(part.split('=', 1)[1])
        return min_value, max_value

    def get_property_type(self, field, properties_type_set=None):
        if properties_type_set is None or not isinstance(properties_type_set, dict):
            properties_type_set = self.properties_type_set
        if isinstance(properties_type_set, dict):
            return properties_type_set.get(field, 'str')
        else:
            return 'str'

    def get_random_from_base(self, field):
        # Seleccionar aleatoriamente un valor del campo correspondiente en la base de datos
        values_for_field = [entry[field] for entry in self.base_collection if field in entry]
        if values_for_field:
            return random.choice(values_for_field)
        return None  # Si no hay valores disponibles para esa clave

    def generate_unique_value(self, field, config):
        """
        Asigna un valor único pre-generado para el campo.
        """
        if field not in self.unique_values:
            raise ValueError(f"El campo '{field}' no tiene valores únicos pre-generados.")

        if self.unique_indices[field] >= len(self.unique_values[field]):
            raise ValueError(f"Se han agotado los valores únicos para el campo '{field}'.")

        value = self.unique_values[field][self.unique_indices[field]]
        self.unique_indices[field] += 1

        if self.unique_indices[field] % 10000 == 0:
            print(f"Se han asignado {self.unique_indices[field]} valores únicos para el campo '{field}'.")

        return value
    def get_nested_field_type(self, parent_field, sub_field):
        # Obtener el tipo de campo anidado desde properties_type_set
        nested_types = self.properties_type_set.get(parent_field, {})
        if isinstance(nested_types, list) and len(nested_types) > 0:
            nested_types = nested_types[0]  # Asumiendo que es una lista de un dict
        return nested_types.get(sub_field, 'str')

    def generate_field(self, field, field_config, field_type, context, properties_type_set):
        # Manejar arreglos heterogéneos
        if field == 'intSubTypeName':
            config = {'generator': 'subtype'}
            return self.generate_single_value(config, context)
        if isinstance(field_config, dict) and 'array_elements' in field_config:
            array_elements = []
            element_configs = field_config['array_elements']
            
            for element_config_dict in element_configs:
                # Cada element_config_dict es un diccionario con subcampos y sus generadores
                element = {}
                for sub_field, sub_generator_str in element_config_dict.items():
                    sub_field_type = self.get_nested_field_type(field, sub_field)
                    # Generar el valor para el subcampo
                    sub_value = self.generate_field(sub_field, sub_generator_str, sub_field_type, context, properties_type_set)
                    element[sub_field] = sub_value
                array_elements.append(element)
            
            return array_elements
        else:
            # Parse field_config solo si no es un arreglo heterogéneo
            config = self.parse_config(field_config)
            config['field_type'] = field_type  # Agregar el tipo de campo a la configuración

            # Manejar valores únicos
            if config.get('unique', False):
                return self.generate_unique_value(field, config)     

            # Verificar si el campo es un arreglo
            if field_type == 'array' or config.get('is_array'):
                if config.get('size_random'):
                    # Tamaño aleatorio entre size_min y size_max
                    size_min = config.get('size_min', 1)
                    size_max = config.get('size_max', 5)
                    array_size = random.randint(size_min, size_max)
                elif config.get('size') is not None:
                    # Tamaño fijo especificado
                    array_size = config['size']
                else:
                    # Tamaño predeterminado si no se especifica
                    array_size = 1

                array_elements = []
                for _ in range(array_size):
                    element = self.generate_array_element(config)
                    array_elements.append(element)
                
                # Verificar si se debe concatenar el arreglo en una cadena
                concatenator = config.get('concatenator')
                if concatenator is not None and field_type == 'str':
                    return concatenator.join(array_elements)
                else:
                    return array_elements
            else:
                # Generar un solo valor basado en la configuración
                return self.generate_single_value(config, context)

    def generate_array_element(self, config):
        element_type = config.get('type', 'word')  # Predeterminado a 'word' si no se especifica
        if element_type == 'name':
            return self.faker.name()
        elif element_type == 'word':
            return self.faker.word()
        elif element_type == 'int':
            min_value = config.get('min', 0)
            max_value = config.get('max', 100)
            return random.randint(min_value, max_value)
        elif element_type == 'float':
            return round(random.uniform(0, 100), config.get('right_digits', 2))
        elif element_type == 'url':
            return self.faker.url()
        elif element_type == 'date':
            return self.faker.date().isoformat()
        else:
            return self.faker.word()

    def generate_single_value(self, config, context):
        generator = config.get('generator')
        value_type = config.get('type')
        field_type = config.get('field_type', 'str')

        if generator == 'choice':
            values = config.get('values', [])
            if values:
                return random.choice(values)
            else:
                return None
        elif generator == 'random':
            if value_type == 'user_name':
                return self.faker.user_name()
            elif value_type == 'first_name':
                return self.faker.first_name()
            elif value_type == 'last_name':
                return self.faker.last_name()
            elif value_type == 'email':
                return self.faker.email()
            elif value_type == 'phone_number':
                return self.faker.phone_number()
            elif value_type == 'url':
                return self.faker.url()
            elif value_type == 'sentence':
                return self.faker.sentence()
            elif value_type == 'word':
                return self.faker.word()
            elif value_type == 'job_title':
                return self.faker.job()
            elif value_type == 'float':
                min_val = config.get('min', 0.0)
                max_val = config.get('max', 100.0)
                return round(random.uniform(min_val, max_val), 2)
            elif value_type == 'int':
                min_val = config.get('min', 0)
                max_val = config.get('max', 100)
                return random.randint(min_val, max_val)
            elif value_type == 'date':
                return self.faker.date()  # Corrección aplicada aquí
            elif value_type == 'choice_values':
                # Manejar valores de elección pasados de forma diferente
                values = config.get('values', [])
                if values:
                    return random.choice(values)
                else:
                    return None
            else:
                # Si no se especifica un tipo conocido, intenta obtener un valor de la colección base
                value_from_base = self.get_random_from_base(value_type)
                if value_from_base is not None:
                    return value_from_base
                else:
                    return self.faker.word()
        elif generator == 'pyfloat':
            return self.generate_pyfloat(config)
        elif generator == 'subtype':
            type_name = context.get('intTypeName', 'otro')
            return self.generate_subtype_name(type_name)
        else:
            # Generación de valor predeterminado basado en el tipo de campo
            if field_type == 'str':
                return self.faker.word()
            elif field_type == 'int':
                return random.randint(0, 100)
            elif field_type == 'float':
                return round(random.uniform(0, 100), 2)
            elif field_type == 'date':
                return self.faker.date()  # Corrección aplicada aquí también si es necesario
            else:
                return self.faker.word()

    def generate_pyfloat(self, config):
        # Generar un número flotante basado en la configuración
        allowed_keys = {'left_digits', 'right_digits', 'positive', 'min_value', 'max_value'}
        pyfloat_params = {k: v for k, v in config.items() if k in allowed_keys}
        return self.faker.pyfloat(**pyfloat_params)

    def parse_config(self, field_config):
        config = {}
        if isinstance(field_config, str):
            # Usar shlex para dividir la cadena, respetando comillas
            parts = shlex.split(field_config)
            
            # Valores predeterminados
            config['generator'] = None
            config['type'] = None
            config['is_array'] = False
            config['size'] = None
            config['size_random'] = False
            config['size_min'] = None
            config['size_max'] = None
            config['concatenator'] = None  # Nuevo parámetro para el concatenador
            config['min'] = None
            config['max'] = None
            config['values'] = None  # Nuevo parámetro para valores predefinidos
            config['extension_from'] = None
            config['unique'] = False
            # Lista de tipos conocidos
            known_types = [
                'username', 'password', 'email', 'phone', 'ethAddress',
                'nemotecnic', 'pin', 'name', 'lastName', 'date_of_birth',
                'dni', 'gender', 'city', 'state', 'country', 'street_address',
                'latitude', 'longitude', 'building_number', 'company',
                'paragraph', 'sentence', 'url', 'file_name', 'tax_id',
                'license_number', 'date_past', 'date_future', 'organization_type',
                'int', 'word', 'contract_code', 'digital_signature', 'transaction_id', 'file_extension'
            ]
            i = 0
            while i < len(parts):
                part = parts[i]
                if part == 'unique':
                    config['unique'] = True
                    i += 1

                elif part == 'random':
                    config['generator'] = 'random'
                    i += 1
                    if i < len(parts):
                        next_part = parts[i]
                        if next_part == 'choice':
                            config['generator'] = 'choice'
                            i += 1
                        elif next_part in known_types:
                            config['type'] = next_part
                            i += 1
                elif part == 'choice':
                    config['generator'] = 'choice'
                    i += 1
                
                elif part in known_types:
                    config['type'] = part
                    i += 1

                elif part.startswith('extension_from='):
                    extension_field = part.split('=', 1)[1]
                    config['extension_from'] = extension_field
                    i += 1
                elif part.startswith('values='):
                    values_str = part.split('=', 1)[1]
                    # Eliminar comillas si están presentes
                    if values_str.startswith(("'", '"')) and values_str.endswith(("'", '"')):
                        values_str = values_str[1:-1]
                    # Dividir los valores por coma y eliminar espacios en blanco
                    values_list = [v.strip() for v in values_str.split(',')]
                    config['values'] = values_list
                    i += 1
                elif part == 'array':
                    config['is_array'] = True
                    i += 1
                elif part.startswith('size='):
                    size_value = part.split('=', 1)[1]
                    if size_value == 'random':
                        config['size_random'] = True
                        i += 1
                        # Inicializar valores por defecto para min y max
                        config['size_min'] = 1
                        config['size_max'] = 5
                        while i < len(parts):
                            if parts[i].startswith('min='):
                                config['size_min'] = int(parts[i].split('=', 1)[1])
                            elif parts[i].startswith('max='):
                                config['size_max'] = int(parts[i].split('=', 1)[1])
                            else:
                                break
                            i += 1
                    else:
                        config['size'] = int(size_value)
                        i += 1
                elif part.startswith('min='):
                    config['min'] = int(part.split('=', 1)[1])
                    i += 1
                elif part.startswith('max='):
                    config['max'] = int(part.split('=', 1)[1])
                    i += 1
                elif part.startswith('concatenator='):
                    # Extraer el concatenador, respetando las comillas
                    concatenator_value = part.split('=', 1)[1]
                    if concatenator_value.startswith(("'", '"')) and concatenator_value.endswith(("'", '"')):
                        config['concatenator'] = concatenator_value[1:-1]
                    else:
                        config['concatenator'] = concatenator_value
                    i += 1
                elif part == 'pyfloat':
                    config['generator'] = 'pyfloat'
                    i += 1
                    # Analizar parámetros adicionales
                    while i < len(parts):
                        if '=' in parts[i]:
                            key, value = parts[i].split('=', 1)
                            # Parsear el valor adecuadamente
                            if value.lower() == 'true':
                                config[key] = True
                            elif value.lower() == 'false':
                                config[key] = False
                            else:
                                try:
                                    if '.' in value:
                                        config[key] = float(value)
                                    else:
                                        config[key] = int(value)
                                except ValueError:
                                    config[key] = value  # Mantener como cadena si no se puede parsear
                            i += 1
                        else:
                            break

                else:
                    # Si no se reconoce el part, saltar
                    i += 1
        return config

    def generate_data(self):
        data_list = []
        total = self.config.get('total', 1)
        
        for idx in range(total):
            context = {}  # Inicializamos el contexto para cada registro
            try:
                data = self.generate_nested_data(self.properties_set, self.properties_type_set, context)
                data_list.append(data)
            except ValueError as ve:
                print(f"Error en el registro {idx + 1}: {ve}")
                break  # Detener la generación si se encuentra un error
        return data_list

    def generate_nested_data(self, properties_set, properties_type_set, context):
        data = {}
        for field, field_config in properties_set.items():
            field_type = self.get_property_type(field, properties_type_set)
            if isinstance(field_config, dict):
                if 'array_elements' in field_config:
                    # Campo es un arreglo heterogéneo, procesarlo con generate_field
                    data[field] = self.generate_field(field, field_config, field_type, context, properties_type_set)
                else:
                    # Campo anidado, llamar recursivamente
                    nested_properties_set = field_config
                    nested_properties_type_set = properties_type_set.get(field, {})
                    data[field] = self.generate_nested_data(nested_properties_set, nested_properties_type_set, context)
            else:
                data[field] = self.generate_field(field, field_config, field_type, context, properties_type_set)
                context[field] = data[field]  # Agregar el campo al contexto
        return data

    def generate_tax_id(self):
        locale = self.config.get('locale', 'en_US')
        if locale == 'es_ES':
            return self.generate_spanish_nif()
        elif locale == 'en_US':
            return self.faker.ssn()  # Número de Seguro Social en EE.UU.
        # Añadir más casos para otros locales si es necesario
        else:
            return self.faker.bothify(text='??#########')  # Generador genérico

    def generate_spanish_nif(self):
        # Generar un número aleatorio de 8 dígitos
        number = random.randint(0, 99999999)
        number_str = f"{number:08d}"  # Asegurar que tiene 8 dígitos con ceros a la izquierda
        letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
        letter = letters[number % 23]
        return f"{number_str}{letter}"
    
    def generate_subtype_name(self, type_name):
        subtypes = {
            'vivienda': ['casa', 'apartamento', 'estudio', 'cabaña', 'villa', 'chalet'],
            'vehiculo': ['coche', 'motocicleta', 'camioneta', 'furgoneta', 'autobús']
        }
        return random.choice(subtypes.get(type_name, ['otro']))


# Ejecutar el módulo
def main():
    config_file = '../config/config.json'
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    faker_module = FakerModule(config)
    try:
        generated_data = faker_module.generate_data()
    except ValueError as ve:
        print(f"Error durante la generación de datos: {ve}")
        return

    # Guardar los datos generados en el archivo especificado en la configuración
    output_file = config.get('outputFile', '../output/generated_data.json')  # Valor por defecto si no está definido

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated_data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()

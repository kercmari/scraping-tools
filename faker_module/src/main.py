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
            raise ValueError(f"Locale '{locale}' no es soportado por Faker.") # Obtener el locale de la configuración, por defecto 'en_US'
        self.faker = Faker(locale)  # Configurar Faker con el locale especificado

        # Manejar la colección base
        collection_path = config.get("collection", "")
        self.base_collection = load_base_collection(collection_path)

        self.properties_set = config['propertiesSet']
        self.properties_type_set = config['propertiesTypeSet']
        self.unique_values = {}

        # Inicializar IDs únicos para intDesignerUserId si es necesario
        self.used_user_ids = set()
        user_id_config = self.properties_set.get('intDesignerUserId', '')
        self.user_id_min, self.user_id_max = self.parse_min_max(user_id_config)
        if self.user_id_min is None:
            self.user_id_min = 0
        if self.user_id_max is None:
            self.user_id_max = 1000000

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

    def generate_unique_user_id(self):
        # Generar un ID único para intDesignerUserId
        while True:
            user_id = random.randint(self.user_id_min, self.user_id_max)
            if user_id not in self.used_user_ids:
                self.used_user_ids.add(user_id)
                return user_id

    def generate_unique_value(self, field, config):
        unique_values_set = self.unique_values.setdefault(field, set())
        max_attempts = 10000  # Evitar loops infinitos

        for _ in range(max_attempts):
            value = self.generate_single_value(config, context={})
            if value not in unique_values_set:
                unique_values_set.add(value)
                return value
        raise ValueError(f"No se pudo generar un valor único para el campo '{field}' después de {max_attempts} intentos.")

    def generate_field(self, field, field_config, field_type, context, properties_type_set):
        # Manejar arreglos heterogéneos
        if isinstance(field_config, dict) and 'array_elements' in field_config:
            array_elements = []
            element_types = []
            
            # Obtener los tipos de los elementos desde properties_type_set
            if isinstance(properties_type_set.get(field, {}), dict):
                element_types = properties_type_set[field].get('element_types', [])
            
            for idx, element_config_str in enumerate(field_config['array_elements']):
                element_config = self.parse_config(element_config_str)
                
                # Obtener el tipo de elemento correspondiente
                if idx < len(element_types):
                    element_type = element_types[idx]
                else:
                    element_type = 'str'  # Tipo predeterminado si no está especificado
                
                element_config['field_type'] = element_type
                value = self.generate_single_value(element_config, context)
                array_elements.append(value)
            
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
            return str(random.randint(min_value, max_value))  # Convertir a cadena si se va a concatenar
        elif element_type == 'float':
            return str(random.uniform(0, 100))  # Convertir a cadena si se va a concatenar
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
            if value_type == 'username':
                return self.faker.user_name()
            elif value_type == 'password':
                return self.faker.password()
            elif value_type == 'email':
                return self.faker.email()
            elif value_type == 'phone':
                return self.faker.phone_number()
            elif value_type == 'ethAddress':
                return self.faker.sha256()
            elif value_type == 'nemotecnic':
                return self.faker.sentence()
            elif value_type == 'pin':
                return str(random.randint(1000, 9999))
            elif value_type == 'name':
                return self.faker.first_name()
            elif value_type == 'lastName':
                return self.faker.last_name()
            elif value_type == 'date_of_birth':
                return self.faker.date_of_birth().isoformat()
            elif value_type == 'dni':
                return self.generate_spanish_nif()
            elif value_type == 'gender':
                return random.choice(['masculino', 'femenino'])
            elif value_type == 'city':
                return self.faker.city()
            elif value_type == 'state':
                return self.faker.state()
            elif value_type == 'country':
                return self.faker.country()
            elif value_type == 'street_address':
                return self.faker.street_address()
            elif value_type == 'latitude':
                return str(self.faker.latitude())
            elif value_type == 'longitude':
                return str(self.faker.longitude())
            elif value_type == 'building_number':
                return self.faker.building_number()
            elif value_type == 'company':
                return self.faker.company()
            elif value_type == 'paragraph':
                return self.faker.paragraph()
            elif value_type == 'sentence':
                return self.faker.sentence()
            elif value_type == 'url':
                return self.faker.url()

            elif value_type == 'tax_id':
                return self.generate_tax_id()
            elif value_type == 'license_number':
                return self.faker.bothify(text='???-####')
            elif value_type == 'date_past':
                return self.faker.past_date().isoformat()
            elif value_type == 'date_future':
                return self.faker.future_date().isoformat()
            elif value_type == 'organization_type':
                return random.choice([
                    'organización benéfica',
                    'persona jurídica',
                    'personas naturales',
                    'organizaciones sin fines de lucro',
                    'organizaciones gubernamentales'
                ])
            elif value_type == 'int':
                min_value = config.get('min', 0)
                max_value = config.get('max', 100)
                return random.randint(min_value, max_value)
            elif value_type == 'word':
                return self.faker.word()
            elif value_type == 'contract_code':
                return self.faker.bothify(text='CT-#####')
            elif value_type == 'digital_signature':
                return self.faker.sha256()
            elif value_type == 'transaction_id':
                return self.faker.uuid4()
           
            elif value_type == 'file_name':
                extension = config.get('extension')
                if extension is None:
                    extension_from = config.get('extension_from')
                    if extension_from and extension_from in context:
                        extension = context[extension_from]
                return self.faker.file_name(extension=extension)
            elif value_type == 'file_extension':
                return self.faker.file_extension()
            else:
                # Si no se especifica un tipo conocido, intenta obtener un valor de la colección base
                value_from_base = self.get_random_from_base(value_type)
                if value_from_base is not None:
                    return value_from_base
                else:
                    return self.faker.word()
        elif generator == 'pyfloat':
            return self.generate_pyfloat(config)
        else:
            # Generación de valor predeterminado basado en el tipo de campo
            if field_type == 'str':
                return self.faker.word()
            elif field_type == 'int':
                return random.randint(0, 100)
            elif field_type == 'float':
                return random.uniform(0, 100)
            elif field_type == 'date':
                return self.faker.date().isoformat()
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
                        elif next_part in ['username', 'password', 'email', 'phone', 'ethAddress',
                                           'nemotecnic', 'pin', 'name', 'lastName', 'date_of_birth',
                                           'dni', 'gender', 'city', 'state', 'country', 'street_address',
                                           'latitude', 'longitude', 'building_number', 'company',
                                           'paragraph', 'sentence', 'url', 'file_name', 'tax_id',
                                           'license_number', 'date_past', 'date_future', 'organization_type',
                                           'int', 'word', 'contract_code', 'digital_signature', 'transaction_id', 'file_extension']:
                            config['type'] = next_part
                            i += 1
                elif part == 'choice':
                    config['generator'] = 'choice'
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
                    i += 1
        return config

    def generate_data(self):
        data_list = []
        total = self.config.get('total', 1)
        
        for _ in range(total):
            context = {}  # Inicializamos el contexto para cada registro
            data = self.generate_nested_data(self.properties_set, self.properties_type_set, context)
            data_list.append(data)
        
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

# Ejecutar el módulo
def main():
    config_file = '../config/config.json'
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    faker_module = FakerModule(config)
    generated_data = faker_module.generate_data()

    # Guardar los datos generados en el archivo especificado en la configuración
    output_file = config.get('outputFile', '../output/generated_data.json')  # Valor por defecto si no está definido

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated_data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()

import json
import random
import re

class JSONVerifier:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.json_data_path = self.config.get("json_data_path")
        self.output_data_path = self.config.get("output_data_path")
        self.required_keys = self.config.get("required_keys", [])
        self.key_types = self.parse_key_types(self.config.get("key_types", {}))
        self.empty_allowed_keys = self.config.get("empty_allowed_keys", [])
        self.separator = self.config.get("separator", ",")
        self.random_values = self.config.get("random_values", {})
        self.random_number_ranges = self.config.get("random_number_ranges", {})
        self.max_empty_keys = self.config.get("max_empty_keys", 0)
        self.key_char_limits = self.config.get("key_char_limits", {})

    def load_config(self, config_path):
        with open(config_path, 'r') as config_file:
            return json.load(config_file)

    def load_json_data(self):
        with open(self.json_data_path, 'r') as json_file:
            data = json.load(json_file)
            if not isinstance(data, list):
                raise ValueError("JSON data should be a list of dictionaries.")
            
            valid_data = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    valid_data.append(item)
                else:
                    print(f"Ignoring item at index {i}: {item} (Type: {type(item).__name__})")
            
            return valid_data

    def save_json_data(self, data):
        with open(self.output_data_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def parse_key_types(self, key_types_config):
        type_mapping = {
            "str": str,
            "int": int,
            "list": list,
            "dict": dict,
            "float": float,
            "bool": bool
        }
        return {key: type_mapping[value] for key, value in key_types_config.items()}

    def verify_and_transform_json(self, data_list):
        verified_data_list = []
        for data in data_list:
            if isinstance(data, dict):
                trimmed_data = {k.strip(): v for k, v in data.items()}  # Trim spaces from keys
                verified_data = self.transform_data(trimmed_data)
                if self.count_empty_keys(verified_data) <= self.max_empty_keys:
                    verified_data_list.append(verified_data)
            else:
                print(f"Warning: Expected dictionary but got {type(data).__name__}")
                continue  # Skip this entry if it's not a dictionary
        return verified_data_list

    def transform_data(self, data):
        verified_data = {}
        for key in self.required_keys:
            snake_key = camel_to_snake(key)
            if snake_key in data:
                if not isinstance(data[snake_key], self.key_types.get(key, type(data[snake_key]))):
                    verified_data[key] = self.assign_random_value(key)
                else:
                    verified_data[key] = self.apply_char_limit(key, data[snake_key])
                if self.is_empty(verified_data[key]) and key in self.random_values:
                    verified_data[key] = self.assign_random_value(key)  # Fill empty or "undefined" with random value
            else:
                verified_data[key] = self.apply_char_limit(key, self.assign_random_value(key))
        
        return verified_data

    def count_empty_keys(self, data):
        """
        Count how many keys in the data have empty values.
        """
        return sum(1 for key in data if self.is_empty(data[key]))

    def is_empty(self, value):
        """
        Check if a value is considered empty, including "undefined".
        """
        return value in [None, "", [], {}, 0, "undefined"]

    def assign_random_value(self, key):
        """
        Assign a random value either from a predefined list or from a number range.
        """
        if key in self.random_values:
            return random.choice(self.random_values[key])
        if key in self.random_number_ranges:
            min_val, max_val = self.random_number_ranges[key]
            return random.randint(min_val, max_val)
        if self.key_types.get(key) == str:
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
        return None

    def apply_char_limit(self, key, value):
        """
        Apply character limit to a string if specified in the config.
        """
        if isinstance(value, str) and key in self.key_char_limits:
            return value[:self.key_char_limits[key]]
        return value

    def transform_to_type(self, value, target_type, key=None):
        if target_type == str and isinstance(value, list):
            return self.separator.join(map(str, value))
        if target_type == str and isinstance(value, str):
            # Verificar si el string es un array de algún tipo
            if value.startswith('[') and value.endswith(']'):
                try:
                    # Convertir el string a lista
                    value_list = json.loads(value)
                    if isinstance(value_list, list):
                        return self.separator.join(map(str, value_list))
                except json.JSONDecodeError:
                    return value  # No se pudo convertir, devolver el valor original
        if target_type == int:
            if isinstance(value, str):
                # Extract numeric part from the string and convert to int
                numeric_value = re.sub(r'\D', '', value)
                if numeric_value:
                    return int(numeric_value)
                else:
                    return self.assign_random_value(key)  # Assign random number if no numeric value found
            if isinstance(value, (float, int)):
                return int(value)
        if isinstance(value, target_type):
            return value
        try:
            return target_type(value)
        except (ValueError, TypeError):
            return self.assign_random_value(key)

def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

# Example usage
if __name__ == "__main__":
    verifier = JSONVerifier("config.json")
    json_data_list = verifier.load_json_data()
    
    try:
        verified_data_list = verifier.verify_and_transform_json(json_data_list)
        verifier.save_json_data(verified_data_list)
        print(f"Verified data saved to {verifier.output_data_path}")
    except ValueError as e:
        print(f"Error: {e}")

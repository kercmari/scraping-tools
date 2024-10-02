import json
import random
import re
from faker import Faker

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
        self.random_float_ranges = self.config.get("random_float_ranges", {})
        self.operations = self.config.get("operations", [])
        self.max_empty_keys = self.config.get("max_empty_keys", 0)
        self.key_char_limits = self.config.get("key_char_limits", {})
        self.faker_values = self.config.get("fakerValues", {})  # Adding fakerValues support

        self.faker = Faker()

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
                verified_data = self.apply_operations(verified_data)  # Apply math operations
                if self.count_empty_keys(verified_data) <= self.max_empty_keys:
                    verified_data_list.append(verified_data)
            else:
                print(f"Warning: Expected dictionary but got {type(data).__name__}")
                continue  # Skip this entry if it's not a dictionary
        return verified_data_list

    def transform_data(self, data):
        verified_data = {}
        for key in self.required_keys:
            # Look for the key in different formats
            found_key, value = self.find_key(data, key)
            if found_key:
                if not isinstance(value, self.key_types.get(key, type(value))):
                    verified_data[key] = self.assign_random_value(key)
                else:
                    verified_data[key] = self.apply_char_limit(key, value)
                if self.is_empty(verified_data[key]):
                    verified_data[key] = self.assign_random_value(key)  # Fill empty with random value
            else:
                verified_data[key] = self.assign_random_value(key)
        
        # Apply faker values if the key is missing
        for faker_key, faker_instruction in self.faker_values.items():
            if faker_key not in verified_data or self.is_empty(verified_data[faker_key]):
                verified_data[faker_key] = self.apply_faker_value(faker_instruction)
        
        return verified_data

    def apply_operations(self, data):
        """
        Applies mathematical operations defined in the configuration for null values.
        """
        for operation in self.operations:
            if operation['type'] == 'math':
                key = operation['key']
                precision = operation.get('precision')
                if self.is_empty(data.get(key)):
                    try:
                        problem = operation['problem']
                        # Replace variables in the problem with their values from `data`
                        for var in re.findall(r'\b\w+\b', problem):
                            if var in data:
                                problem = problem.replace(var, str(data[var]))
                        # Evaluate the math expression
                        result = eval(problem)
                        if precision is not None:
                            result = round(result, precision)
                        data[key] = result
                    except Exception as e:
                        print(f"Error applying operation for key '{key}': {e}")
        return data

    def apply_faker_value(self, faker_instruction):
        """
        Use the faker library to generate a value based on the instruction.
        """
        try:
            # Ensure we use correct Faker methods, e.g., "city", "name"
            faker_method = getattr(self.faker, faker_instruction)
            return faker_method()
        except AttributeError:
            print(f"Error: Faker does not support the instruction '{faker_instruction}'")
            return None

    def find_key(self, data, required_key):
        """
        Looks for a key in camelCase, snake_case, and SCREAMING_SNAKE_CASE formats.
        Returns the found key and its value, or (None, None) if not found.
        """
        camel = required_key
        snake = camel_to_snake(required_key)
        screaming_snake = snake.upper()
        
        for variant in [camel, snake, screaming_snake]:
            if variant in data:
                return variant, data[variant]
        return None, None

    def count_empty_keys(self, data):
        """
        Count how many keys in the data have empty values.
        """
        return sum(1 for key in data if self.is_empty(data[key]))

    def is_empty(self, value):
        """
        Checks if a value is considered empty, including "undefined".
        """
        return value in [None, "", [], {}, "undefined"]

    def assign_random_value(self, key):
        """
        Assign a random value from predefined lists, number ranges, float ranges, or generate a random string.
        """
        if key in self.faker_values:
            return self.apply_faker_value(self.faker_values[key])
        if key in self.random_values:
            return random.choice(self.random_values[key])
        if key in self.random_number_ranges:
            min_val, max_val = self.random_number_ranges[key]
            return random.randint(min_val, max_val)
        if key in self.random_float_ranges:
            min_val, max_val = self.random_float_ranges[key]
            return random.uniform(min_val, max_val)
        if self.key_types.get(key) == str:
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
        return None

    def apply_char_limit(self, key, value):
        """
        Apply a character limit to a string if specified in the configuration.
        """
        if isinstance(value, str) and key in self.key_char_limits:
            return value[:self.key_char_limits[key]]
        return value

    def transform_to_type(self, value, target_type, key=None):
        if target_type == str and isinstance(value, list):
            return self.separator.join(map(str, value))
        if target_type == str and isinstance(value, str):
            if value.startswith('[') and value.endswith(']'):
                try:
                    value_list = json.loads(value)
                    if isinstance(value_list, list):
                        return self.separator.join(map(str, value_list))
                except json.JSONDecodeError:
                    return value
        if target_type == int:
            if isinstance(value, str):
                numeric_value = re.sub(r'\D', '', value)
                if numeric_value:
                    return int(numeric_value)
                else:
                    return self.assign_random_value(key)
            if isinstance(value, (float, int)):
                return int(value)
        if isinstance(value, bool):
            return value  # Do not modify boolean values
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

def screaming_snake_to_snake(screaming_snake_str):
    return screaming_snake_str.lower()

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

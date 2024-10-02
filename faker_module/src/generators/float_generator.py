import random
from .base_generator import ValueGenerator

class FloatGenerator(ValueGenerator):
    def generate(self, config):
        min_value = config.get('min_value', 0)
        max_value = config.get('max_value', 1)
        right_digits = config.get('right_digits', 2)
        return round(random.uniform(min_value, max_value), right_digits)

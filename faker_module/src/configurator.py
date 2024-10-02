from generators.float_generator import FloatGenerator

class Configurator:
    def __init__(self, config):
        self.config = config

    def get_generator(self, field_config):
        if 'pyfloat' in field_config:
            return FloatGenerator()
        # Aquí se pueden agregar más tipos como 'pyint', 'pydecimal', etc.
        else:
            raise ValueError("Tipo de generador no soportado.")

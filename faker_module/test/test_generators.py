import unittest
from src.generators.float_generator import FloatGenerator

class TestFloatGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = FloatGenerator()

    def test_generate_float(self):
        config = {
            'min_value': 100000,
            'max_value': 9900000,
            'right_digits': 2
        }
        value = self.generator.generate(config)
        self.assertTrue(100000 <= value <= 9900000)
        self.assertEqual(len(str(value).split('.')[1]), 2)

if __name__ == '__main__':
    unittest.main()

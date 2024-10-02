import unittest
from src.main import FakerModule

class TestFakerModule(unittest.TestCase):
    def setUp(self):
        self.config = {
            "total": 100000,
            "properties": {
                "finResIncome": "pyfloat min_value=100000 max_value=9900000",
                "finResCreditRate": "pyfloat min_value=0 max_value=1 right_digits=2",
                "finResAssets": "pyfloat min_value=100000 max_value=9900000",
                "finResDebts": "pyfloat min_value=10000 max_value=99999"
            }
        }
        self.faker_module = FakerModule(self.config)

    def test_generate_data(self):
        data = self.faker_module.generate_data()
        self.assertIn('finResIncome', data)
        self.assertIn('finResCreditRate', data)
        self.assertIn('finResAssets', data)
        self.assertIn('finResDebts', data)

if __name__ == '__main__':
    unittest.main()

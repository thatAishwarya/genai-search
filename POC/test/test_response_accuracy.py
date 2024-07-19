import unittest
from response_generator import ResponseGenerator

class TestResponseAccuracy(unittest.TestCase):
    def setUp(self):
        self.generator = ResponseGenerator()

    def test_response(self):
        context = "The financial regulator ensures compliance with financial laws."
        query = "What does the financial regulator do?"
        response = self.generator.generate_response(context, query)
        self.assertIn("ensures compliance", response)

if __name__ == '__main__':
    unittest.main()

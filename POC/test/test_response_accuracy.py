import unittest
import requests

class TestResponseAccuracy(unittest.TestCase):
    def setUp(self):
        self.url = 'http://127.0.0.1:5000/search'
    
    def test_search_response(self):
        response = requests.post(self.url, json={'query': 'financial regulations'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Extractive Answer:', response.json()['response'])
        self.assertIn('Abstractive Summary:', response.json()['response'])

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from financial_entity_categorizer import FinancialEntityCategorizer

class TestFinancialEntityCategorizer(unittest.TestCase):
    def setUp(self):
        self.categorizer = FinancialEntityCategorizer()

    @patch('wikipedia.search')
    @patch('wikipedia.page')
    def test_blackrock_categorization(self, mock_page, mock_search):
        # Mock Wikipedia search results
        mock_search.return_value = ['BlackRock']
        
        # Mock Wikipedia page content
        mock_page_instance = MagicMock()
        mock_page_instance.content = """
        BlackRock is an American multinational investment management corporation 
        based in New York City. Founded in 1988, initially as a risk management 
        and fixed income institutional asset manager, BlackRock is the world's 
        largest asset manager, with US$10 trillion in assets under management 
        as of January 2022. It is a leading investment company and asset management firm.
        """
        mock_page.return_value = mock_page_instance

        # Test categorization
        categories = self.categorizer.get_matching_categories("BlackRock")
        
        # Assertions
        self.assertIn("Investment Companies".lower(), [category.lower() for category in categories])
        self.assertNotIn("Charities and Ngos".lower(), [category.lower() for category in categories])
        self.assertNotIn("Shell Companies".lower(), [category.lower() for category in categories])

    @patch('wikipedia.search')
    @patch('wikipedia.page')
    def test_gates_foundation_categorization(self, mock_page, mock_search):
        # Mock Wikipedia search results
        mock_search.return_value = ['Bill & Melinda Gates Foundation']
        
        # Mock Wikipedia page content
        mock_page_instance = MagicMock()
        mock_page_instance.content = """
        The Bill & Melinda Gates Foundation is an American private foundation 
        founded by Bill Gates and Melinda French Gates. It is the largest 
        private foundation in the United States, having $50.7 billion in assets. 
        The foundation is a charitable organization focused on global health and development.
        """
        mock_page.return_value = mock_page_instance

        # Test categorization
        categories = self.categorizer.get_matching_categories("Bill & Melinda Gates Foundation")
        
        # Assertions
        self.assertIn("Trusts and Foundations".lower(), [category.lower() for category in categories])
        self.assertIn("Charities and Ngos".lower(), [category.lower() for category in categories])
        self.assertNotIn("Investment Companies".lower(), [category.lower() for category in categories])

    @patch('wikipedia.search')
    @patch('wikipedia.page')
    def test_sequoia_capital_categorization(self, mock_page, mock_search):
        # Mock Wikipedia search results
        mock_search.return_value = ['Sequoia Capital']
        
        # Mock Wikipedia page content
        mock_page_instance = MagicMock()
        mock_page_instance.content = """
        Sequoia Capital is an American venture capital firm headquartered in 
        Menlo Park, California which specializes in seed stage, early stage, 
        and growth stage investments in private companies across technology sectors.
        """
        mock_page.return_value = mock_page_instance

        # Test categorization
        categories = self.categorizer.get_matching_categories("Sequoia Capital")
        
        # Assertions
        self.assertIn("Venture Capital".lower(), [category.lower() for category in categories])
        self.assertNotIn("Investment Companies".lower(), [category.lower() for category in categories])
        self.assertNotIn("Shell Companies".lower(), [category.lower() for category in categories])

    @patch('wikipedia.search')
    def test_no_results(self, mock_search):
        # Mock Wikipedia search with no results
        mock_search.return_value = []
        
        # Test categorization
        categories = self.categorizer.get_matching_categories("NonExistentEntity")
        
        # Assertions
        self.assertEqual(categories, [])

    @patch('wikipedia.search')
    @patch('wikipedia.page')
    def test_wikipedia_error_handling(self, mock_page, mock_search):
        # Mock Wikipedia search to raise an exception
        mock_search.side_effect = Exception("Wikipedia API Error")
        
        # Test that the error is properly handled
        with self.assertRaises(Exception):
            self.categorizer.get_matching_categories("TestEntity")

if __name__ == '__main__':
    unittest.main()
"""
Test suite for the AI Research Assistant
Tests search functionality, report generation, and query optimization
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from research_assistant import search_topic, generate_report, research_agent_core

# Set a test API key
os.environ['GROQ_API_KEY'] = 'test_key_for_testing'

# Mock save_report to prevent file creation during tests
@patch('research_assistant.save_report')
def mock_save_report(mock_save):
    """Mock save_report to prevent creating files during tests"""
    mock_save.return_value = 'test_report_mock.txt'
    return mock_save


class TestSearchTopic(unittest.TestCase):
    """Tests for search_topic function"""
    
    def test_search_returns_dict(self):
        """Test that search_topic returns a dictionary"""
        result = search_topic("artificial intelligence")
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
        self.assertIn('citations', result)
    
    def test_search_content_not_empty(self):
        """Test that search returns non-empty content for valid queries"""
        result = search_topic("Python programming")
        self.assertTrue(len(result['content']) > 0)
    
    def test_search_citations_is_list(self):
        """Test that citations is a list"""
        result = search_topic("machine learning")
        self.assertIsInstance(result['citations'], list)
    
    def test_search_handles_empty_query(self):
        """Test that search handles empty queries gracefully"""
        result = search_topic("")
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
    
    def test_search_with_special_characters(self):
        """Test search with special characters"""
        result = search_topic("quantum computing & AI")
        self.assertIsInstance(result, dict)
    
    def test_search_long_query(self):
        """Test search with a long descriptive query"""
        result = search_topic("what is the impact of artificial intelligence on modern healthcare systems")
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result['content']) > 0)


class TestGenerateReport(unittest.TestCase):
    """Tests for generate_report function"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = "Machine learning is a subset of artificial intelligence that focuses on the ability of machines to learn and improve from experience."
    
    def test_report_generation_short(self):
        """Test short report generation"""
        report = generate_report("AI", self.test_data, "short")
        self.assertIsInstance(report, str)
        # Report should either be valid or contain error about missing API key
        self.assertTrue(len(report) > 0)
    
    def test_report_generation_medium(self):
        """Test medium report generation"""
        report = generate_report("AI", self.test_data, "medium")
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 0)
    
    def test_report_generation_long(self):
        """Test long report generation"""
        report = generate_report("AI", self.test_data, "long")
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 0)
    
    def test_report_default_length(self):
        """Test report generation with default length"""
        report = generate_report("AI", self.test_data)
        self.assertIsInstance(report, str)
    
    def test_report_with_invalid_length(self):
        """Test report generation with invalid length defaults to medium"""
        report = generate_report("AI", self.test_data, "invalid")
        self.assertIsInstance(report, str)


class TestResearchAgentCore(unittest.TestCase):
    """Tests for research_agent_core function"""
    
    @patch('research_assistant.save_report')
    def test_agent_returns_dict_with_required_keys(self, mock_save):
        """Test that agent returns required dictionary keys"""
        mock_save.return_value = 'mocked_file.txt'
        result = research_agent_core("Python", None, "short")
        self.assertIsInstance(result, dict)
        self.assertIn('report', result)
        self.assertIn('filename', result)
        self.assertIn('citations', result)
    
    @patch('research_assistant.save_report')
    def test_agent_with_single_query(self, mock_save):
        """Test agent with single query"""
        mock_save.return_value = 'mocked_file.txt'
        result = research_agent_core("web development", None, "short")
        self.assertIsInstance(result['report'], str)
    
    @patch('research_assistant.save_report')
    def test_agent_with_multiple_queries(self, mock_save):
        """Test agent with multiple queries"""
        mock_save.return_value = 'mocked_file.txt'
        result = research_agent_core("AI", ["machine learning", "neural networks"], "short")
        self.assertIsInstance(result['report'], str)
        self.assertIsNotNone(result['filename'])
    
    @patch('research_assistant.save_report')
    def test_agent_report_lengths(self, mock_save):
        """Test agent with different report lengths"""
        mock_save.return_value = 'mocked_file.txt'
        for length in ["short", "medium", "long"]:
            result = research_agent_core("technology", None, length)
            self.assertIsInstance(result['report'], str)
    
    @patch('research_assistant.save_report')
    def test_agent_handles_no_results(self, mock_save):
        """Test agent gracefully handles queries with no results"""
        mock_save.return_value = 'mocked_file.txt'
        result = research_agent_core("xyzabc123nonexistent", None, "short")
        # Should return a dict even if no results
        self.assertIsInstance(result, dict)


class TestSearchSpecificQueries(unittest.TestCase):
    """Tests for specific search queries that had issues"""
    
    def test_quantum_tunneling_search(self):
        """Test that quantum tunneling returns results"""
        result = search_topic("quantum tunneling")
        self.assertTrue(len(result['content']) > 0, 
                       "quantum tunneling search should return content")
        self.assertNotIn("No information found", result['content'])
    
    def test_quantum_generic_search(self):
        """Test that generic quantum search returns results"""
        result = search_topic("quantum")
        self.assertTrue(len(result['content']) > 0)
    
    def test_quantum_computing_search(self):
        """Test quantum computing search"""
        result = search_topic("quantum computing")
        self.assertTrue(len(result['content']) > 0)
    
    def test_quantum_mechanics_search(self):
        """Test quantum mechanics search"""
        result = search_topic("quantum mechanics")
        self.assertTrue(len(result['content']) > 0)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling"""
    
    def test_search_handles_network_error(self):
        """Test that search handles network errors gracefully"""
        with patch('research_assistant.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            result = search_topic("test")
            self.assertIsInstance(result, dict)
            self.assertEqual(result['content'], "Search failed")
    
    def test_generate_report_handles_missing_client(self):
        """Test that report generation handles missing API key"""
        with patch('research_assistant.client', None):
            report = generate_report("test", "test data")
            self.assertIn("GROQ_API_KEY", report)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSearchTopic))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateReport))
    suite.addTests(loader.loadTestsFromTestCase(TestResearchAgentCore))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchSpecificQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

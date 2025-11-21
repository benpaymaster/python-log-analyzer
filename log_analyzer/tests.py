import unittest
from .analyzer import analyze_logs

class TestLogAnalyzer(unittest.TestCase):
    """
    Tests for the log analysis functions, demonstrating commitment to quality and
    testable code.
    """
    def test_basic_analysis(self):
        """Test with a simple, clean dataset for counting and average calculation."""
        logs = """
2025-11-21 10:00:01 | TradingEngine | INFO | 12.5ms
2025-11-21 10:00:02 | DataFeed | SUCCESS | 50.0ms
2025-11-21 10:00:03 | TradingEngine | INFO | 17.5ms
"""
        result = analyze_logs(logs)
        
        # Check TradingEngine stats
        self.assertEqual(result['TradingEngine']['total_events'], 2)
        # Average latency for TradingEngine: (12.5 + 17.5) / 2 = 15.0
        self.assertEqual(result['TradingEngine']['average_latency_ms'], 15.00)
        self.assertEqual(result['TradingEngine']['error_rate'], '0.00%')
        
        # Check DataFeed stats
        self.assertEqual(result['DataFeed']['average_latency_ms'], 50.00)
        self.assertEqual(result['DataFeed']['total_events'], 1)

    def test_error_counting(self):
        """Test counting errors and calculating the error rate correctly."""
        logs = """
2025-11-21 10:00:05 | DataFeed | ERROR | 5.0ms
2025-11-21 10:00:06 | DataFeed | SUCCESS | 10.0ms
2025-11-21 10:00:07 | MarketData | ERROR | 2.0ms
2025-11-21 10:00:08 | MarketData | ERROR | 3.0ms
2025-11-21 10:00:09 | MarketData | SUCCESS | 5.0ms
"""
        result = analyze_logs(logs)
        
        # DataFeed: 1 error out of 2 events = 50.00%
        self.assertEqual(result['DataFeed']['error_rate'], '50.00%')
        
        # MarketData: 2 errors out of 3 events = 66.67%
        self.assertEqual(result['MarketData']['total_events'], 3)
        self.assertEqual(result['MarketData']['error_rate'], '66.67%')
        
        # MarketData latency: (2.0 + 3.0 + 5.0) / 3 = 3.333...
        self.assertEqual(result['MarketData']['average_latency_ms'], 3.33)

    def test_empty_input(self):
        """Test with empty log data or only whitespace."""
        logs = ""
        result = analyze_logs(logs)
        self.assertEqual(result, {})

        logs_whitespace = "    \n\n  "
        result_whitespace = analyze_logs(logs_whitespace)
        self.assertEqual(result_whitespace, {})
        
    def test_malformed_lines(self):
        """Test that the parser skips malformed lines gracefully."""
        logs = """
2025-11-21 10:00:01 | ServiceA | SUCCESS | 10.0ms
2025-11-21 10:00:02 | ServiceB | ERROR
2025-11-21 10:00:03 | ServiceA | INFO | 5.0ms
"""
        result = analyze_logs(logs)
        # Service A should have 2 events
        self.assertEqual(result['ServiceA']['total_events'], 2)
        # Service B should be ignored
        self.assertNotIn('ServiceB', result)
        # Avg latency for ServiceA: (10.0 + 5.0) / 2 = 7.5
        self.assertEqual(result['ServiceA']['average_latency_ms'], 7.50)
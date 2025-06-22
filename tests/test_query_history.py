"""Tests for the query history module."""

import unittest
from unittest.mock import MagicMock, patch
import datetime
import sys
import os
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import query_history


class TestQueryHistory(unittest.TestCase):
    """Test cases for query history."""

    def test_display_results_empty(self):
        """Test displaying empty results."""
        # Arrange
        results = []
        
        # Act & Assert
        with patch('sys.stdout', new=StringIO()) as fake_out:
            query_history.display_results(results)
            self.assertEqual("No matching commands found.\n", fake_out.getvalue())

    def test_display_results_with_data(self):
        """Test displaying results with data."""
        # Arrange
        timestamp = datetime.datetime(2023, 2, 15, 12, 0)
        results = [
            {
                "command": "ls -la",
                "exit_code": 0,
                "stdout": "total 0\ndrwxr-xr-x  2 user  group  64 Feb 15 12:00 .\n",
                "stderr": "",
                "execution_time_seconds": 0.1,
                "timestamp": timestamp,
                "ai_category": "file_system",
                "ai_description": "List all files with detailed information"
            }
        ]
        
        # Act
        with patch('sys.stdout', new=StringIO()) as fake_out:
            query_history.display_results(results)
            output = fake_out.getvalue()
            
            # Assert
            self.assertIn("[1] Command: ls -la", output)
            self.assertIn(f"    Executed at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", output)
            self.assertIn("    Exit code: 0", output)
            self.assertIn("    Execution time: 0.10 seconds", output)
            self.assertIn("    Category: file_system", output)
            self.assertIn("    Description: List all files with detailed information", output)
            self.assertIn("    Output: total 0", output)

    @patch('query_history.connect_to_mongodb')
    @patch('query_history.build_query_filters')
    @patch('query_history.query_commands')
    @patch('query_history.clean_old_collections')
    @patch('sys.argv', ['query_history.py', '--search', 'ls'])
    def test_main_function(self, mock_clean, mock_query, mock_build_filters, mock_connect):
        """Test the main function."""
        # Arrange
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        mock_clean.return_value = []
        
        mock_filters = {"command": {"$regex": "ls", "$options": "i"}}
        mock_build_filters.return_value = mock_filters
        
        timestamp = datetime.datetime(2023, 2, 15, 12, 0)
        mock_results = [
            {
                "command": "ls -la",
                "exit_code": 0,
                "stdout": "test output",
                "stderr": "",
                "execution_time_seconds": 0.1,
                "timestamp": timestamp
            }
        ]
        mock_query.return_value = mock_results
        
        # Act
        with patch('query_history.display_results') as mock_display:
            query_history.main()
            
            # Assert
            mock_connect.assert_called_once()
            mock_build_filters.assert_called_once()
            mock_query.assert_called_once_with(mock_db, mock_filters, 10, 30)
            mock_display.assert_called_once_with(mock_results)


if __name__ == '__main__':
    unittest.main()

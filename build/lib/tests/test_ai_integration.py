"""Tests for the AI integration module."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ai_integration


class TestAIIntegration(unittest.TestCase):
    """Test cases for AI integration."""

    @patch('requests.post')
    def test_analyze_command_success(self, mock_post):
        """Test successful command analysis."""
        # Arrange
        command = "ls -la"
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': '{"category": "file_management", "description": "List all files with detailed information"}'
        }
        mock_post.return_value = mock_response
        
        # Act
        category, description = ai_integration.analyze_command(command, "test_model")
        
        # Assert
        self.assertEqual("file_management", category)
        self.assertEqual("List all files with detailed information", description)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(ai_integration.OLLAMA_API_URL, args[0])
        self.assertEqual("test_model", kwargs["json"]["model"])
        self.assertEqual(command, kwargs["json"]["prompt"].strip().split("\n")[-1].replace("Command: ", ""))

    @patch('requests.post')
    def test_analyze_command_api_error(self, mock_post):
        """Test handling API errors."""
        # Arrange
        command = "ls -la"
        
        # Mock the API response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Act
        category, description = ai_integration.analyze_command(command)
        
        # Assert
        self.assertEqual("uncategorized", category)
        self.assertIn("Failed to categorize", description)

    @patch('requests.post')
    def test_analyze_command_json_error(self, mock_post):
        """Test handling JSON parsing errors."""
        # Arrange
        command = "ls -la"
        
        # Mock the API response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'This is not JSON'
        }
        mock_post.return_value = mock_response
        
        # Act
        category, description = ai_integration.analyze_command(command)
        
        # Assert
        self.assertEqual("uncategorized", category)
        self.assertIn("Response format error", description)

    @patch('requests.post')
    def test_analyze_command_connection_error(self, mock_post):
        """Test handling connection errors."""
        # Arrange
        command = "ls -la"
        
        # Mock a connection error
        mock_post.side_effect = Exception("Connection error")
        
        # Act
        category, description = ai_integration.analyze_command(command)
        
        # Assert
        self.assertEqual("uncategorized", category)
        self.assertIn("Error analyzing command", description)


if __name__ == '__main__':
    unittest.main()

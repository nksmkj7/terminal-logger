"""Tests for the terminal logger module."""

import unittest
from unittest.mock import MagicMock, patch
import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import terminal_logger


class TestTerminalLogger(unittest.TestCase):
    """Test cases for terminal logger."""

    def test_execute_command_success(self):
        """Test executing a command successfully."""
        # Arrange
        command = "echo 'test'"
        
        # Act
        result = terminal_logger.execute_command(command)
        
        # Assert
        self.assertEqual(command, result["command"])
        self.assertEqual(0, result["exit_code"])
        self.assertEqual("test\n", result["stdout"])
        self.assertEqual("", result["stderr"])
        self.assertIsInstance(result["execution_time_seconds"], float)
        self.assertIsInstance(result["timestamp"], datetime.datetime)

    def test_execute_command_failure(self):
        """Test executing a command that fails."""
        # Arrange
        command = "nonexistentcommand"
        
        # Act
        result = terminal_logger.execute_command(command)
        
        # Assert
        self.assertEqual(command, result["command"])
        self.assertNotEqual(0, result["exit_code"])
        self.assertEqual("", result["stdout"])
        self.assertNotEqual("", result["stderr"])  # Should contain error message
        self.assertIsInstance(result["execution_time_seconds"], float)
        self.assertIsInstance(result["timestamp"], datetime.datetime)

    def test_execute_command_exception(self):
        """Test handling an exception during command execution."""
        # Arrange
        command = "echo 'test'"
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Test exception")
            
            # Act
            result = terminal_logger.execute_command(command)
            
            # Assert
            self.assertEqual(command, result["command"])
            self.assertEqual(-1, result["exit_code"])
            self.assertEqual("", result["stdout"])
            self.assertEqual("Test exception", result["stderr"])
            self.assertIsInstance(result["execution_time_seconds"], float)
            self.assertIsInstance(result["timestamp"], datetime.datetime)

    @patch('terminal_logger.connect_to_mongodb')
    @patch('terminal_logger.execute_command')
    @patch('terminal_logger.analyze_command')
    @patch('terminal_logger.store_command_result')
    @patch('terminal_logger.clean_old_collections')
    @patch('sys.argv', ['terminal_logger.py', 'echo test'])
    def test_main_function(self, mock_clean, mock_store, mock_analyze, mock_execute, mock_connect):
        """Test the main function."""
        # Arrange
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        mock_execute.return_value = {
            "command": "echo test",
            "exit_code": 0,
            "stdout": "test\n",
            "stderr": "",
            "execution_time_seconds": 0.1,
            "timestamp": datetime.datetime.now()
        }
        
        mock_analyze.return_value = ("file_system", "Echo command that displays the text 'test'")
        mock_store.return_value = "test_id"
        mock_clean.return_value = []
        
        # Act
        with patch('sys.exit') as mock_exit:
            terminal_logger.main()
            
            # Assert
            mock_connect.assert_called_once()
            mock_execute.assert_called_once()
            mock_analyze.assert_called_once()
            mock_store.assert_called_once()
            mock_exit.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()

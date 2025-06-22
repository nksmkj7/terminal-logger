"""Tests for the database maintenance module."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import maintain_db


class TestMaintainDB(unittest.TestCase):
    """Test cases for database maintenance."""

    @patch('maintain_db.connect_to_mongodb')
    @patch('maintain_db.clean_old_collections')
    @patch('sys.argv', ['maintain_db.py', '--retention', '60'])
    def test_main_function_clean(self, mock_clean, mock_connect):
        """Test the main function with cleaning."""
        # Arrange
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        mock_clean.return_value = ["command_history_2023_01_01", "command_history_2023_01_02"]
        
        # Act
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = maintain_db.main()
            
            # Assert
            self.assertEqual(0, result)
            mock_connect.assert_called_once()
            mock_clean.assert_called_once_with(mock_db, 60)
            output = fake_out.getvalue()
            self.assertIn("Terminal Logger Database Maintenance", output)
            self.assertIn("Retention period: 60 days", output)
            self.assertIn("Dry run: No", output)
            self.assertIn("Removed 2 old collections:", output)
            self.assertIn("command_history_2023_01_01", output)
            self.assertIn("command_history_2023_01_02", output)

    @patch('maintain_db.connect_to_mongodb')
    @patch('maintain_db.datetime')
    @patch('sys.argv', ['maintain_db.py', '--dry-run'])
    def test_main_function_dry_run(self, mock_datetime, mock_connect):
        """Test the main function with dry run."""
        # Arrange
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        # Mock database collections
        mock_db.list_collection_names.return_value = [
            "command_history_2023_01_01",
            "command_history_2023_02_01",
            "some_other_collection"
        ]
        
        # Mock collection document counts
        coll1 = MagicMock()
        coll1.count_documents.return_value = 10
        coll2 = MagicMock()
        coll2.count_documents.return_value = 20
        
        def get_collection(name):
            if name == "command_history_2023_01_01":
                return coll1
            elif name == "command_history_2023_02_01":
                return coll2
            return MagicMock()
            
        mock_db.__getitem__.side_effect = get_collection
        
        # Mock current date to 2023-03-01
        mock_datetime.now.return_value.strftime.return_value = "2023-03-01 00:00:00"
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.timedelta.return_value = MagicMock()
        
        # Act
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('maintain_db.datetime') as mock_dt:
                mock_dt.now.return_value.strftime.return_value = "2023-03-01 00:00:00"
                mock_dt.now.return_value = MagicMock()
                mock_dt.timedelta.return_value = MagicMock()
                
                # Mock the cutoff date calculation
                from datetime import datetime, timedelta
                mock_date = datetime(2023, 3, 1)
                mock_cutoff = datetime(2023, 2, 1)  # 30 days before
                mock_dt.now.return_value = mock_date
                mock_dt.timedelta.side_effect = lambda days: timedelta(days=days)
                mock_dt.strftime = datetime.strftime
                
                result = maintain_db.main()
                
                # Assert
                self.assertEqual(0, result)
                mock_connect.assert_called_once()
                output = fake_out.getvalue()
                self.assertIn("Terminal Logger Database Maintenance", output)
                self.assertIn("Dry run: Yes", output)
                self.assertIn("Found 2 command history collections:", output)
                self.assertIn("command_history_2023_01_01: 10 documents", output)
                self.assertIn("command_history_2023_02_01: 20 documents", output)
                self.assertIn("Would remove 1 collections:", output)
                self.assertIn("command_history_2023_01_01: 10 documents", output)


if __name__ == '__main__':
    unittest.main()

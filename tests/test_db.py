"""Tests for the database module."""

import datetime
import unittest
from unittest.mock import MagicMock, patch
from pymongo.database import Database

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import db


class TestDB(unittest.TestCase):
    """Test cases for database operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = MagicMock(spec=Database)
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection

    def test_get_collection_for_today(self):
        """Test getting the collection for today."""
        # Arrange
        today = datetime.datetime.now().strftime("%Y_%m_%d")
        expected_name = f"command_history_{today}"

        # Act
        collection = db.get_collection_for_today(self.mock_db)

        # Assert
        self.mock_db.__getitem__.assert_called_with(expected_name)
        self.assertEqual(collection, self.mock_collection)

    def test_collection_exists(self):
        """Test checking if a collection exists."""
        # Arrange
        self.mock_db.list_collection_names.return_value = ["command_history_2023_01_01", "command_history_2023_01_02"]

        # Act & Assert
        self.assertTrue(db.collection_exists(self.mock_db, "command_history_2023_01_01"))
        self.assertFalse(db.collection_exists(self.mock_db, "command_history_2023_01_03"))

    def test_clean_old_collections(self):
        """Test cleaning old collections."""
        # Arrange
        self.mock_db.list_collection_names.return_value = [
            "command_history_2023_01_01",
            "command_history_2023_01_15",
            "command_history_2023_02_01",
            "some_other_collection"
        ]
        
        with patch('db.datetime') as mock_datetime:
            # Set current date to 2023-02-15
            mock_datetime.now.return_value = datetime.datetime(2023, 2, 15)
            mock_datetime.strftime = datetime.datetime.strftime
            mock_datetime.timedelta = datetime.timedelta
            
            # Act
            removed = db.clean_old_collections(self.mock_db, 30)
            
            # Assert
            self.assertEqual(1, len(removed))
            self.assertEqual("command_history_2023_01_01", removed[0])
            self.mock_db.drop_collection.assert_called_once_with("command_history_2023_01_01")

    def test_store_command_result(self):
        """Test storing a command result."""
        # Arrange
        result = {"command": "ls", "exit_code": 0}
        self.mock_collection.insert_one.return_value.inserted_id = "test_id"
        
        with patch('db.get_collection_for_today') as mock_get_collection:
            mock_get_collection.return_value = self.mock_collection
            
            # Act
            id_str = db.store_command_result(self.mock_db, result)
            
            # Assert
            self.mock_collection.insert_one.assert_called_once_with(result)
            self.assertEqual("test_id", id_str)

    def test_query_commands(self):
        """Test querying commands."""
        # Arrange
        self.mock_db.list_collection_names.return_value = [
            "command_history_2023_02_01",
            "command_history_2023_02_02",
            "command_history_2023_02_03"
        ]
        
        # Mock collection query results
        mock_result1 = {"command": "ls", "timestamp": datetime.datetime(2023, 2, 3, 12, 0)}
        mock_result2 = {"command": "pwd", "timestamp": datetime.datetime(2023, 2, 2, 12, 0)}
        
        # Configure mocks for the three collections
        collection1 = MagicMock()
        collection1.find().sort().limit.return_value = [mock_result1]
        
        collection2 = MagicMock()
        collection2.find().sort().limit.return_value = [mock_result2]
        
        collection3 = MagicMock()
        collection3.find().sort().limit.return_value = []
        
        # Configure the db mock to return different collections
        def get_collection(name):
            if name == "command_history_2023_02_03":
                return collection1
            elif name == "command_history_2023_02_02":
                return collection2
            elif name == "command_history_2023_02_01":
                return collection3
            return MagicMock()
            
        self.mock_db.__getitem__.side_effect = get_collection
        
        with patch('db.datetime') as mock_datetime:
            # Set current date to 2023-02-15
            mock_datetime.now.return_value = datetime.datetime(2023, 2, 15)
            mock_datetime.min = datetime.datetime.min
            mock_datetime.strftime = datetime.datetime.strftime
            mock_datetime.timedelta = datetime.timedelta
            
            # Act
            results = db.query_commands(self.mock_db, {}, 10, 30)
            
            # Assert
            self.assertEqual(2, len(results))
            # Results should be sorted by timestamp (newest first)
            self.assertEqual("ls", results[0]["command"])
            self.assertEqual("pwd", results[1]["command"])

    def test_build_query_filters(self):
        """Test building query filters."""
        # Test with search
        filters = db.build_query_filters(search="ls")
        self.assertEqual({"command": {"$regex": "ls", "$options": "i"}}, filters)
        
        # Test with success
        filters = db.build_query_filters(success=True)
        self.assertEqual({"exit_code": 0}, filters)
        
        # Test with failed
        filters = db.build_query_filters(failed=True)
        self.assertEqual({"exit_code": {"$ne": 0}}, filters)
        
        # Test with category
        filters = db.build_query_filters(category="file")
        self.assertEqual({"ai_category": {"$regex": "file", "$options": "i"}}, filters)
        
        # Test with multiple filters
        filters = db.build_query_filters(search="git", success=True, category="version")
        self.assertEqual({
            "command": {"$regex": "git", "$options": "i"},
            "exit_code": 0,
            "ai_category": {"$regex": "version", "$options": "i"}
        }, filters)


if __name__ == '__main__':
    unittest.main()

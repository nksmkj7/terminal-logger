"""Database connection and operations for terminal logger."""

import sys
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection details from environment variables
DEFAULT_MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
DEFAULT_MONGODB_PORT = int(os.environ.get("MONGODB_PORT", "27017"))
DEFAULT_MONGODB_DB = os.environ.get("MONGODB_DB", "terminal_logger")
DEFAULT_MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME", "admin")
DEFAULT_MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "admin")


def connect_to_mongodb(host: str = None, port: int = None, db_name: str = None) -> Database:
    """Connect to MongoDB and return the database instance."""
    try:
        mongodb_host = host or DEFAULT_MONGODB_HOST
        mongodb_port = port or DEFAULT_MONGODB_PORT
        mongodb_db = db_name or DEFAULT_MONGODB_DB
        mongodb_username = DEFAULT_MONGODB_USERNAME
        mongodb_password = DEFAULT_MONGODB_PASSWORD
        
        # Create connection with authentication if username is provided
        if mongodb_username:
            uri = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_db}?authSource=admin"
            client = MongoClient(uri)
        else:
            # Use simple connection without authentication
            client = MongoClient(mongodb_host, mongodb_port)
            
        return client[mongodb_db]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)


def get_collection_for_today(db: Database) -> Collection:
    """Get or create the collection for today's date."""
    today = datetime.now().strftime("%Y_%m_%d")
    collection_name = f"command_history_{today}"
    return db[collection_name]


def collection_exists(db: Database, collection_name: str) -> bool:
    """Check if a collection exists in the database."""
    return collection_name in db.list_collection_names()


def clean_old_collections(db: Database, retention_days: int = 30) -> List[str]:
    """
    Remove collections older than the specified retention period.
    
    Args:
        db: MongoDB database instance
        retention_days: Number of days to keep collections (default: 30)
        
    Returns:
        List of removed collection names
    """
    removed_collections = []
    
    # Get all collections
    all_collections = db.list_collection_names()
    
    # Filter command history collections
    history_collections = [c for c in all_collections if c.startswith("command_history_")]
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime("%Y_%m_%d")
    
    # Remove old collections
    for collection_name in history_collections:
        # Extract date from collection name
        try:
            # Format is command_history_YYYY_MM_DD
            date_part = collection_name[16:]  # Extract YYYY_MM_DD part
            
            # Compare with cutoff date
            if date_part < cutoff_str:
                db.drop_collection(collection_name)
                removed_collections.append(collection_name)
        except Exception:
            # Skip collections that don't match the expected format
            continue
    
    return removed_collections


def store_command_result(db: Database, result: Dict[str, Any]) -> str:
    """Store the command result in MongoDB and return the inserted ID."""
    collection = get_collection_for_today(db)
    inserted = collection.insert_one(result)
    return str(inserted.inserted_id)


def query_commands(
    db: Database, 
    filters: Dict[str, Any] = None, 
    limit: int = 10, 
    days_to_search: int = 30
) -> List[Dict[str, Any]]:
    """
    Query command history based on filters.
    
    Args:
        db: MongoDB database instance
        filters: Query filters to apply
        limit: Maximum number of results to return
        days_to_search: Number of days to search back (default: 30)
        
    Returns:
        List of command history records
    """
    if filters is None:
        filters = {}
    
    # Calculate the start date for the search
    start_date = datetime.now() - timedelta(days=days_to_search)
    start_date_str = start_date.strftime("%Y_%m_%d")
    
    # Get all collections
    all_collections = db.list_collection_names()
    
    # Filter command history collections within the date range
    history_collections = [
        c for c in all_collections 
        if c.startswith("command_history_") and c[16:] >= start_date_str
    ]
    
    # Sort collections by date (newest first)
    history_collections.sort(reverse=True)
    
    results = []
    remaining_limit = limit
    
    # Query each collection
    for collection_name in history_collections:
        if remaining_limit <= 0:
            break
            
        collection = db[collection_name]
        collection_results = list(collection.find(filters).sort("timestamp", -1).limit(remaining_limit))
        
        results.extend(collection_results)
        remaining_limit = limit - len(results)
    
    # Sort results by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
    
    # Limit to the requested number
    return results[:limit]


def build_query_filters(
    search: str = None, 
    days: int = None, 
    success: bool = False, 
    failed: bool = False,
    category: str = None
) -> Dict[str, Any]:
    """Build MongoDB query filters based on input parameters."""
    filters = {}
    
    if search:
        filters["command"] = {"$regex": search, "$options": "i"}
    
    # Note: days filter is handled by query_commands function now
    
    if success:
        filters["exit_code"] = 0
    
    if failed:
        filters["exit_code"] = {"$ne": 0}
        
    if category:
        filters["ai_category"] = {"$regex": category, "$options": "i"}
    
    return filters

# Add this new function to your existing db.py

def get_collections_in_date_range(db: Database, start_date: datetime) -> List[str]:
    """Get command history collection names within a date range."""
    all_collections = db.list_collection_names()
    start_date_str = start_date.strftime("%Y_%m_%d")
    
    # Filter collections by date format
    history_collections = [
        c for c in all_collections 
        if c.startswith("command_history_") and c[16:] >= start_date_str
    ]
    
    # Sort collections by date (newest first)
    history_collections.sort(reverse=True)
    return history_collections

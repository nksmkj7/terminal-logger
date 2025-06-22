#!/usr/bin/env python3

import argparse
import sys
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from db import connect_to_mongodb, query_commands, build_query_filters, clean_old_collections

# Load environment variables from .env file
load_dotenv()


def display_results(results: List[Dict[str, Any]]):
    """Display the query results in a readable format."""
    if not results:
        print("No matching commands found.")
        return
    
    for i, result in enumerate(results, 1):
        print(f"[{i}] Command: {result['command']}")
        print(f"    Executed at: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Exit code: {result['exit_code']}")
        print(f"    Execution time: {result['execution_time_seconds']:.2f} seconds")
        
        # Display AI analysis if available
        if "ai_category" in result and "ai_description" in result:
            print(f"    Category: {result['ai_category']}")
            print(f"    Description: {result['ai_description']}")
        
        if result["stdout"] and len(result["stdout"]) > 100:
            print(f"    Output: {result['stdout'][:100]}...")
        elif result["stdout"]:
            print(f"    Output: {result['stdout']}")
            
        if result["stderr"]:
            print(f"    Error: {result['stderr']}")
            
        print()


def main():
    parser = argparse.ArgumentParser(description="Query command history from MongoDB")
    parser.add_argument("--host", default=os.environ.get("MONGODB_HOST", "localhost"), help="MongoDB host (default: localhost or $MONGODB_HOST)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MONGODB_PORT", 27017)), help="MongoDB port (default: 27017 or $MONGODB_PORT)")
    parser.add_argument("--db", default=os.environ.get("MONGODB_DB", "terminal_logger"), help="MongoDB database name (default: terminal_logger or $MONGODB_DB)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results to show (default: 10)")
    parser.add_argument("--search", help="Search for commands containing this text")
    parser.add_argument("--days", type=int, default=int(os.environ.get("RETENTION_DAYS", 30)), help="Search commands from the last N days (default: 30 or $RETENTION_DAYS)")
    parser.add_argument("--success", action="store_true", help="Show only successful commands (exit code 0)")
    parser.add_argument("--failed", action="store_true", help="Show only failed commands (non-zero exit code)")
    parser.add_argument("--category", help="Filter commands by AI-assigned category")
    parser.add_argument("--clean", action="store_true", help="Clean old collections before querying")
    parser.add_argument("--retention", type=int, default=int(os.environ.get("RETENTION_DAYS", 30)), help="Number of days to retain command history (default: 30 or $RETENTION_DAYS)")
    
    args = parser.parse_args()
    
    # Connect to MongoDB
    db = connect_to_mongodb(args.host, args.port, args.db)
    
    # Clean old collections if requested
    if args.clean:
        removed = clean_old_collections(db, args.retention)
        if removed:
            print(f"Cleaned {len(removed)} old collections: {', '.join(removed)}")
    
    # Build the filters
    filters = build_query_filters(
        args.search, 
        None,  # Days filter is now handled by query_commands 
        args.success, 
        args.failed,
        args.category
    )
    
    # Query and display results
    results = query_commands(db, filters, args.limit, args.days)
    display_results(results)


if __name__ == "__main__":
    main()

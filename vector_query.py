#!/usr/bin/env python3
"""Vector-based natural language query for terminal history."""

import argparse
import sys
from typing import Dict, Any, List

from db import connect_to_mongodb
from vector_search import vector_search
from query_history import display_results


def main():
    parser = argparse.ArgumentParser(description="Natural language search for command history")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    parser.add_argument("--days", type=int, default=30, help="Search commands from the last N days (default: 30)")
    
    args = parser.parse_args()
    
    # Connect to MongoDB
    db = connect_to_mongodb()
    
    print(f"Searching for: '{args.query}'")
    print("---")
    
    # Perform vector search
    results = vector_search(db, args.query, args.limit, args.days)
    
    # Display results
    display_results(results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

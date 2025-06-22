#!/usr/bin/env python3
"""
Maintenance script for terminal-logger database.
This script can be run as a cron job to clean up old collections.
"""

import argparse
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

from db import connect_to_mongodb, clean_old_collections

# Load environment variables from .env file
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Maintain terminal-logger database")
    parser.add_argument("--host", default=os.environ.get("MONGODB_HOST", "localhost"), help="MongoDB host (default: localhost or $MONGODB_HOST)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MONGODB_PORT", 27017)), help="MongoDB port (default: 27017 or $MONGODB_PORT)")
    parser.add_argument("--db", default=os.environ.get("MONGODB_DB", "terminal_logger"), help="MongoDB database name (default: terminal_logger or $MONGODB_DB)")
    parser.add_argument("--retention", type=int, default=int(os.environ.get("RETENTION_DAYS", 30)), help="Number of days to retain command history (default: 30 or $RETENTION_DAYS)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually removing collections")
    
    args = parser.parse_args()
    
    # Connect to MongoDB
    db = connect_to_mongodb(args.host, args.port, args.db)
    
    print(f"Terminal Logger Database Maintenance")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Retention period: {args.retention} days")
    print(f"Dry run: {'Yes' if args.dry_run else 'No'}")
    print("---")
    
    if args.dry_run:
        # Get all collections
        all_collections = db.list_collection_names()
        
        # Filter command history collections
        history_collections = [c for c in all_collections if c.startswith("command_history_")]
        history_collections.sort()
        
        print(f"Found {len(history_collections)} command history collections:")
        for collection in history_collections:
            count = db[collection].count_documents({})
            print(f"  - {collection}: {count} documents")
        
        # Calculate which would be removed
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=args.retention)
        cutoff_str = cutoff_date.strftime("%Y_%m_%d")
        
        would_remove = [c for c in history_collections if c[16:] < cutoff_str]
        would_remove.sort()
        
        print(f"\nWould remove {len(would_remove)} collections:")
        for collection in would_remove:
            count = db[collection].count_documents({})
            print(f"  - {collection}: {count} documents")
    else:
        # Actually remove old collections
        removed = clean_old_collections(db, args.retention)
        print(f"Removed {len(removed)} old collections:")
        for collection in sorted(removed):
            print(f"  - {collection}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

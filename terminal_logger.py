#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import sys
from typing import Dict, Any
from dotenv import load_dotenv

from db import connect_to_mongodb, store_command_result, clean_old_collections
from ai_integration import analyze_command
from vector_search import add_vector_to_result

# Load environment variables from .env file
load_dotenv()

def execute_command(command: str,original_dir: str = None) -> Dict[str, Any]:
    """Execute the given command and return the result details."""
    start_time = datetime.datetime.now()
    execution_dir = original_dir if original_dir else os.getcwd()
    
    try:
        # Execute the command and capture output
        process = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=execution_dir,
        )
        
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "command": command,
            "exit_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "execution_time_seconds": execution_time,
            "timestamp": start_time,
        }
    except Exception as e:
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "command": command,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "execution_time_seconds": execution_time,
            "timestamp": start_time,
        }


def main():
    # Get default values for AI and retention settings (DB settings now come from db.py)
    default_ai_model = os.environ.get("AI_MODEL", "")
    default_retention = int(os.environ.get("RETENTION_DAYS", "30"))

    parser = argparse.ArgumentParser(description="Execute terminal commands and log them to MongoDB")
    parser.add_argument("command", help="The command to execute")
    parser.add_argument("--original-dir", help="Directory where the command was originally invoked")
    # Removed --host, --port, and --db arguments as they won't be used for overriding
    parser.add_argument("--ai-model", default=default_ai_model, help=f"Ollama model to use for command analysis (default: {default_ai_model})")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI analysis of the command")
    parser.add_argument("--retention", type=int, default=default_retention, help=f"Number of days to retain command history (default: {default_retention})")
    parser.add_argument("--clean", action="store_true", help="Clean old collections before executing the command")
    
    args = parser.parse_args()
    
    # Connect to MongoDB (using only environment variables from db.py)
    db = connect_to_mongodb()

    
    # Clean old collections if requested
    if args.clean:
        removed = clean_old_collections(db, args.retention)
        if removed:
            print(f"Cleaned {len(removed)} old collections: {', '.join(removed)}", file=sys.stderr)
    
    # Execute the command
    result = execute_command(args.command, args.original_dir)
    result["dir"] = args.original_dir if args.original_dir else os.getcwd()
    # If AI analysis is enabled, analyze the command
    if not args.no_ai:
        try:
            print("Analyzing command with AI...", file=sys.stderr)
            category, description = analyze_command(args.command, args.ai_model)
            result["ai_category"] = category
            result["ai_description"] = description
            print(f"Category: {category}", file=sys.stderr)
            print(f"Description: {description}", file=sys.stderr)
            print("---", file=sys.stderr)
        except Exception as e:
            print(f"AI analysis failed: {e}", file=sys.stderr)
            result["ai_category"] = "error"
            result["ai_description"] = f"AI analysis failed: {str(e)}"
    else:
        result["ai_category"] = "uncategorized"
        result["ai_description"] = "AI analysis skipped"
        
    result = add_vector_to_result(result)
    
    # Print command output to terminal
    if result["stdout"]:
        print(result["stdout"], end="")
    if result["stderr"]:
        print(result["stderr"], file=sys.stderr, end="")
    
    # Store the result in MongoDB
    record_id = store_command_result(db, result)
    
    # Exit with the same code as the executed command
    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()

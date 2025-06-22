# Terminal Logger

A Python utility that executes terminal commands and logs them to MongoDB for future reference. It includes AI-powered command analysis using locally running Ollama models.

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. Clone this repository
2. Set up a virtual environment (requires Python 3.6+):
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
4. Alternatively, use the provided setup script:
   ```bash
   # On Linux/macOS:
   bash setup_venv.sh
   
   # This will create the virtual environment and install dependencies
   ```

5. Ensure MongoDB is running on your system
6. Ensure Ollama is running with the DeepSeek model (or another model of your choice)
   ```bash
   # Install Ollama from https://ollama.ai/
   # Pull the DeepSeek model
   ollama pull deepseek
   ```

### Option 2: System-wide Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure MongoDB is running on your system
4. Ensure Ollama is running with the DeepSeek model

## Usage

Make sure your virtual environment is activated if you're using one.

### Executing and Logging Commands

To execute a command and store it in MongoDB:

```bash
python terminal_logger.py "your command here"
```

For example:

```bash
python terminal_logger.py "ls -la"
```

Additional options:
- `--host`: MongoDB host (default: localhost)
- `--port`: MongoDB port (default: 27017)
- `--db`: MongoDB database name (default: terminal_logger)
- `--ai-model`: Ollama model to use for command analysis (default: deepseek)
- `--no-ai`: Skip AI analysis of the command
- `--retention DAYS`: Number of days to retain command history (default: 30)
- `--clean`: Clean old collections before executing the command

### Querying Command History

To view your command history:

```bash
python query_history.py
```

Options:
- `--search "text"`: Search for commands containing the specified text
- `--days N`: Search commands from the last N days (default: 30)
- `--success`: Show only successful commands (exit code 0)
- `--failed`: Show only failed commands (non-zero exit code)
- `--category "category"`: Filter by AI-assigned category
- `--limit N`: Limit to N results (default: 10)
- `--host`: MongoDB host (default: localhost)
- `--port`: MongoDB port (default: 27017)
- `--db`: MongoDB database name (default: terminal_logger)
- `--clean`: Clean old collections before querying
- `--retention DAYS`: Number of days to retain command history (default: 30)

### Database Maintenance

Terminal Logger now uses a separate MongoDB collection for each day. Collections older than
the retention period (default: 30 days) can be automatically removed.

To manually clean old collections:

```bash
python maintain_db.py
```

Options:
- `--host`: MongoDB host (default: localhost)
- `--port`: MongoDB port (default: 27017)
- `--db`: MongoDB database name (default: terminal_logger)
- `--retention DAYS`: Number of days to retain command history (default: 30)
- `--dry-run`: Show what would be done without actually removing collections

To set up automatic cleaning, add a cron job:

```bash
# Example cron job to run daily at 3:00 AM
0 3 * * * cd /path/to/terminal-logger && /path/to/venv/bin/python maintain_db.py
```

## Environment Configuration

This project supports configuration via a `.env` file in the project root. You can copy `.env.example` to `.env` and adjust the values as needed:

```bash
cp .env.example .env
```

**Supported environment variables:**
- `MONGODB_HOST`: MongoDB host (default: localhost)
- `MONGODB_PORT`: MongoDB port (default: 27017)
- `MONGODB_DB`: MongoDB database name (default: terminal_logger)
- `RETENTION_DAYS`: Number of days to retain command history (default: 30)
- `AI_MODEL`: Ollama model to use for command analysis (default: deepseek)
- `OLLAMA_API_URL`: Ollama API endpoint (default: http://localhost:11434/api/generate)

All scripts will automatically load these values if present in your `.env` file.

## Examples

Execute a command and log it with AI analysis:
```bash
python terminal_logger.py "find . -name '*.py'"
```

Skip AI analysis:
```bash
python terminal_logger.py --no-ai "ls -la"
```

Use a different Ollama model:
```bash
python terminal_logger.py --ai-model llama3 "ps aux | grep python"
```

Query recent failed commands:
```bash
python query_history.py --failed --days 7
```

Search command history:
```bash
python query_history.py --search "git commit"
```

Filter by AI-assigned category:
```bash
python query_history.py --category "file management"
```

Clean collections older than 60 days:
```bash
python maintain_db.py --retention 60
```

## Development

If you want to develop this tool further, you can install it in development mode:

```bash
# Make sure your virtual environment is activated
pip install -e .
```

### Understanding setup.py

The `setup.py` file in this project enables several powerful features:

1. **Installable Package**: Makes terminal-logger installable as a Python package using pip
   ```bash
   # Install directly from the directory
   pip install .
   
   # Install in development mode (changes to code reflect immediately)
   pip install -e .
   ```

2. **Command-line Scripts**: Provides the commands `terminal-logger` and `query-history` that can be run from anywhere once installed
   ```bash
   # After installation, you can simply type:
   terminal-logger "ls -la"
   query-history --search "git"
   ```

3. **Dependency Management**: Automatically installs required dependencies
   ```bash
   # Install the package and all its dependencies
   pip install .
   ```

4. **Distribution**: Allows you to build distributable packages
   ```bash
   # Create a distributable package
   python setup.py sdist bdist_wheel
   
   # Upload to PyPI (if you want to share it)
   pip install twine
   twine upload dist/*
   ```

5. **Metadata**: Provides important metadata about your project for package indexes and documentation

### Running Tests

Terminal Logger comes with a comprehensive test suite. To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. tests/

# Run a specific test file
pytest tests/test_db.py

# Run a specific test
pytest tests/test_db.py::TestDB::test_query_commands
```

Tests are organized to match the module structure of the application, making it easy to locate and run specific tests.

"""Integration with Ollama for AI-powered command analysis."""

import json
import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, Tuple

# Load environment variables from .env file
load_dotenv()

# Default Ollama endpoint and model from environment variables
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
DEFAULT_AI_MODEL = os.environ.get("AI_MODEL", "deepseek")

def analyze_command(command: str, model: str = None) -> Tuple[str, str]:
    """
    Analyze a shell command using the Ollama API and return a category and description.
    
    Args:
        command: The shell command to analyze
        model: The Ollama model to use (default: from env or 'deepseek')
        
    Returns:
        Tuple containing (category, description)
    """
    if model is None:
        model = DEFAULT_AI_MODEL
    prompt = f"""
Analyze the following shell command and provide:
1. A single category it belongs to (file management, network, system administration, data processing, etc.)
2. A brief description explaining what this command does in 1-2 sentences.

Format your response as a JSON object with keys 'category' and 'description'.

Command: {command}
"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=1000
        )
        
        if response.status_code != 200:
            return "uncategorized", f"Failed to categorize: API returned status {response.status_code}"
        
        # Parse the response
        result = response.json()
        response_text = result.get('response', '')
        
        # Extract JSON from the response
        # Sometimes LLM responses include extra text before/after the JSON
        try:
            # First, try to find JSON-like structure using braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > 0:
                json_str = response_text[start_idx:end_idx]
                ai_response = json.loads(json_str)
                
                category = ai_response.get('category', 'uncategorized')
                description = ai_response.get('description', 'No description provided')
                
                return category, description
            else:
                return "uncategorized", "Response format error: No JSON structure found"
                
        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to a simple response
            return "uncategorized", "Received non-JSON response from AI model"
            
    except requests.exceptions.RequestException as e:
        return "uncategorized", f"Failed to connect to Ollama API: {str(e)}"
    except Exception as e:
        return "uncategorized", f"Error analyzing command: {str(e)}"

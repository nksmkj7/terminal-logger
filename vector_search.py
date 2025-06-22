"""Vector embedding and search functionality for terminal logger."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List, Optional
from pymongo.database import Database

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> List[float]:
    """Generate a vector embedding for the given text."""
    embedding = model.encode(text)
    return embedding.tolist()  # Convert numpy array to list for MongoDB storage

def create_command_vector(command: str, description: str = "") -> List[float]:
    """Create a combined vector for command and description."""
    # Combine command and description for a richer embedding
    combined_text = f"{command} {description}".strip()
    return generate_embedding(combined_text)

def add_vector_to_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add vector embedding to command result."""
    command = result["command"]
    description = result.get("ai_description", "")
    
    # Generate vector embedding
    vector = create_command_vector(command, description)
    result["vector_embedding"] = vector
    
    return result

def vector_search(
    db: Database, 
    query: str, 
    limit: int = 10, 
    days_to_search: int = 30
) -> List[Dict[str, Any]]:
    """
    Search for commands using vector similarity.
    
    Args:
        db: MongoDB database instance
        query: Natural language query
        limit: Maximum number of results to return
        days_to_search: Number of days to search back
        
    Returns:
        List of command history records sorted by relevance
    """
    # Generate vector for the query
    query_vector = generate_embedding(query)
    
    # Get collections from the date range
    from datetime import datetime, timedelta
    from db import get_collections_in_date_range
    
    start_date = datetime.now() - timedelta(days=days_to_search)
    collections = get_collections_in_date_range(db, start_date)
    
    # Results with similarity scores
    results_with_scores = []
    
    for collection_name in collections:
        collection = db[collection_name]
        
        # Find documents with vector embeddings
        documents = collection.find({"vector_embedding": {"$exists": True}})
        
        for doc in documents:
            doc_vector = doc.get("vector_embedding")
            if doc_vector:
                # Calculate cosine similarity
                similarity = cosine_similarity(query_vector, doc_vector)
                results_with_scores.append((doc, similarity))
    
    # Sort by similarity score (highest first)
    results_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top matches
    return [item[0] for item in results_with_scores[:limit]]

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

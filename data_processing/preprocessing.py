# preprocessing.py
import re
from typing import List, Dict, Any
import unicodedata
import uuid

def normalize_bengali_text(text: str) -> str:
    """Normalize Bengali Unicode text."""
    # Normalize Unicode to NFC form (important for Bengali)
    text = unicodedata.normalize('NFC', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def recursive_character_text_splitter(text: str, chunk_size: int = 512, chunk_overlap: int = 150) -> List[str]:
    """
    Split Bengali text into chunks using character-level splitting with smart overlapping.
    This is more appropriate for Bengali than token-based splitting.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Minimum overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Normalize text first
    text = normalize_bengali_text(text)
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find a good breaking point within the chunk
        end = min(start + chunk_size, len(text))
        
        # If we're not at the end of the text, try to find a better break point
        if end < len(text):
            # Try to break at a sentence boundary first
            sentence_break = text.rfind('।', start, end)  # Bengali sentence end marker
            if sentence_break != -1 and sentence_break > start + chunk_size / 2:
                end = sentence_break + 1
            else:
                # If no good sentence break, try a paragraph break
                para_break = text.rfind('\n', start, end)
                if para_break != -1 and para_break > start + chunk_size / 2:
                    end = para_break
                else:
                    # If no good paragraph break, try a space
                    space_break = text.rfind(' ', start, end)
                    if space_break != -1 and space_break > start + chunk_size / 2:
                        end = space_break
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Move start with overlap, ensuring we don't go backwards
        # Calculate a dynamic overlap that's at least chunk_overlap but might be more
        # at natural sentence boundaries
        if end < len(text):
            # Look for a sentence boundary within the overlap region
            overlap_start = max(end - chunk_overlap * 2, start)  # Look back up to 2x the overlap
            sentence_start = text.rfind('।', overlap_start, end)
            
            if sentence_start != -1 and sentence_start > overlap_start:
                # Found a sentence boundary in the overlap region, start from there
                start = sentence_start + 1
            else:
                # Use the default overlap
                start = max(end - chunk_overlap, start + 1)  # Ensure we always advance
        else:
            start = end
    
    return chunks

def process_bengali_document(doc: Dict[Any, Any], content_field: str = "description", doc_uid: str = None) -> List[Dict]:
    """Process a Bengali document into chunks for indexing."""
    content = doc.get(content_field, "")
    chunks = recursive_character_text_splitter(content)
    # Create chunk documents with metadata
    processed_chunks = []
    # Generate a unique base id for the document if not provided
    base_id = doc_uid if doc_uid is not None else str(uuid.uuid4())
    for i, chunk in enumerate(chunks):
        chunk_doc = {
            "id": f"{base_id}_chunk_{i}",
            "title": doc.get("title", ""),
            "content": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        processed_chunks.append(chunk_doc)
    return processed_chunks

def process_product_comparison(doc: Dict[Any, Any], content_field: str = "description", doc_uid: str = None) -> List[Dict]:
    """Process a product comparison document into chunks for indexing."""
    # Process the product data with the same chunking approach we use for Bengali documents
    content = doc.get(content_field, "")
    chunks = recursive_character_text_splitter(content)
    
    # Create chunk documents with metadata
    processed_chunks = []
    # Generate a unique base id for the document if not provided
    base_id = doc_uid if doc_uid is not None else str(uuid.uuid4())
    
    for i, chunk in enumerate(chunks):
        chunk_doc = {
            "id": f"{base_id}_chunk_{i}",
            "title": doc.get("title", ""),
            "category_left": doc.get("category_left", ""),
            "description_left": doc.get("description_left", ""),
            "title_right": doc.get("title_right", ""),
            "category_right": doc.get("category_right", ""),
            "description_right": doc.get("description_right", ""),
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        processed_chunks.append(chunk_doc)
    
    return processed_chunks


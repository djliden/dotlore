import os
import json
import lancedb
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from dotlore.core import config as config_module

class DotLoreDB:
    """Database interface for DotLore using LanceDB."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the database directory. If None, uses .lore/db.
        """
        if db_path is None:
            db_path = Path('.lore/db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.db = lancedb.connect(str(self.db_path))
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure that all required tables exist."""
        # Main context table for vector search
        if "context" not in self.db.table_names():
            schema = {
                "text": "string",
                "embedding": "float32[1536]",  # Default to OpenAI dimensions
                "source_id": "string",
                "source_type": "string",
                "source_path": "string",
                "chunk_id": "int32",
                "last_updated": "string",
                "raw_chunk": "string"
            }
            self.db.create_table("context", schema=schema)
        
        # Metadata table for tracking sources
        if "sources" not in self.db.table_names():
            schema = {
                "source_id": "string",
                "source_type": "string",
                "source_path": "string",
                "last_updated": "string",
                "content_hash": "string",
                "metadata": "string"  # JSON string for additional metadata
            }
            self.db.create_table("sources", schema=schema)
    
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add chunks to the context table.
        
        Args:
            chunks: List of chunk dictionaries with required fields.
        """
        context_table = self.db.open_table("context")
        context_table.add(chunks)
    
    def add_source(self, source_info: Dict[str, Any]):
        """Add or update a source in the sources table.
        
        Args:
            source_info: Dictionary with source information.
        """
        sources_table = self.db.open_table("sources")
        
        # Check if source already exists
        existing = sources_table.search().where(
            f"source_id = '{source_info['source_id']}'"
        ).to_pandas()
        
        if len(existing) > 0:
            # Update existing source
            sources_table.delete(f"source_id = '{source_info['source_id']}'")
        
        # Convert metadata to JSON string if it's a dict
        if isinstance(source_info.get('metadata'), dict):
            source_info['metadata'] = json.dumps(source_info['metadata'])
        
        sources_table.add([source_info])
    
    def remove_source(self, source_id: str):
        """Remove a source and all its chunks from the database.
        
        Args:
            source_id: Unique identifier for the source.
        """
        # Remove from context table
        context_table = self.db.open_table("context")
        context_table.delete(f"source_id = '{source_id}'")
        
        # Remove from sources table
        sources_table = self.db.open_table("sources")
        sources_table.delete(f"source_id = '{source_id}'")
    
    def list_sources(self):
        """List all sources in the database.
        
        Returns:
            List of source dictionaries.
        """
        sources_table = self.db.open_table("sources")
        return sources_table.search().to_pandas().to_dict('records')
    
    def get_source(self, source_id: str):
        """Get information about a specific source.
        
        Args:
            source_id: Unique identifier for the source.
            
        Returns:
            Source dictionary or None if not found.
        """
        sources_table = self.db.open_table("sources")
        results = sources_table.search().where(
            f"source_id = '{source_id}'"
        ).to_pandas()
        
        if len(results) == 0:
            return None
        
        source_info = results.iloc[0].to_dict()
        
        # Parse metadata JSON if it exists
        if source_info.get('metadata'):
            try:
                source_info['metadata'] = json.loads(source_info['metadata'])
            except json.JSONDecodeError:
                pass
                
        return source_info
    
    def query_context(self, 
                      query_embedding: List[float], 
                      limit: int = 10, 
                      where_clause: Optional[str] = None):
        """Query the context using vector similarity search.
        
        Args:
            query_embedding: Vector embedding of the query.
            limit: Maximum number of results to return.
            where_clause: Optional filter clause.
            
        Returns:
            List of matching context chunks.
        """
        context_table = self.db.open_table("context")
        query = context_table.search(
            query_vector=query_embedding,
            vector_column_name="embedding"
        )
        
        if where_clause:
            query = query.where(where_clause)
        
        # Use hybrid search with BM25 if available
        if hasattr(query, "hybrid"):
            config = config_module.get_config_value()
            reranking_method = config.get("reranking", {}).get("method", "rrf")
            
            query = query.hybrid(
                query=query_embedding,  # Will be converted to text for BM25
                text_column_name="text",
                fusion_method=reranking_method
            )
        
        results = query.limit(limit).to_pandas()
        return results.to_dict('records')
    
    def get_db_stats(self):
        """Get statistics about the database.
        
        Returns:
            Dictionary with database statistics.
        """
        context_table = self.db.open_table("context")
        sources_table = self.db.open_table("sources")
        
        context_count = len(context_table.search().to_pandas())
        sources_count = len(sources_table.search().to_pandas())
        
        # Get unique source types
        source_types = sources_table.search().to_pandas()["source_type"].unique().tolist()
        
        return {
            "chunks_count": context_count,
            "sources_count": sources_count,
            "source_types": source_types
        }

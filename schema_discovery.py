"""
Dynamic Schema Discovery Module
Automatically detects and analyzes database schemas for any dataset
"""

import sqlite3
from typing import List, Dict, Tuple
from enum import Enum

class ColumnType(Enum):
    """Inferred column types"""
    NUMERIC = "numeric"
    TEXT = "text"
    PERCENTAGE = "percentage"
    STATUS = "status"
    CONTACT = "contact"
    DATE = "date"
    UNKNOWN = "unknown"

class SchemaDiscovery:
    """Discover and analyze database schema dynamically"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_tables(self) -> List[str]:
        """Get all tables in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_columns(self, table_name: str) -> List[str]:
        """Get all column names for a table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    
    def infer_column_type(self, table_name: str, column_name: str) -> ColumnType:
        """Infer column type from name and sample data"""
        col_lower = column_name.lower()
        
        # Contact information
        if any(word in col_lower for word in ['phone', 'contact', 'mobile', 'number']):
            return ColumnType.CONTACT
        
        # Email/Address
        if any(word in col_lower for word in ['email', 'address', 'location']):
            return ColumnType.CONTACT
        
        # Percentage fields
        if any(word in col_lower for word in ['percentage', 'percent', 'ratio', 'rate']):
            return ColumnType.PERCENTAGE
        
        # Status fields
        if any(word in col_lower for word in ['status', 'state', 'condition']):
            return ColumnType.STATUS
        
        # Date fields
        if any(word in col_lower for word in ['date', 'birth', 'joining', 'created']):
            return ColumnType.DATE
        
        # Numeric fields
        if any(word in col_lower for word in ['gpa', 'cgpa', 'score', 'marks', 'amount', 'fee', 'count']):
            return ColumnType.NUMERIC
        
        # Try to infer from actual data
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 5")
            samples = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Check if numeric
            if all(isinstance(s, (int, float)) or (isinstance(s, str) and s.replace('.', '').isdigit()) for s in samples if s):
                return ColumnType.NUMERIC
            
            # Check if contains percentage
            if any('%' in str(s) for s in samples if s):
                return ColumnType.PERCENTAGE
            
        except Exception:
            pass
        
        return ColumnType.TEXT
    
    def get_column_metadata(self, table_name: str) -> Dict[str, Dict]:
        """Get metadata for all columns in a table"""
        columns = self.get_columns(table_name)
        metadata = {}
        
        for col in columns:
            col_type = self.infer_column_type(table_name, col)
            # Create natural language variations of column name
            natural_names = self._generate_natural_names(col)
            
            metadata[col] = {
                'type': col_type.value,
                'original_name': col,
                'natural_names': natural_names,
                'display_name': col.replace('_', ' ').title()
            }
        
        return metadata
    
    def _generate_natural_names(self, column_name: str) -> List[str]:
        """Generate natural language variations of column name"""
        names = set()
        
        # Original and lowercase
        names.add(column_name.lower())
        names.add(column_name.replace('_', ' ').lower())
        
        # Remove common prefixes/suffixes
        clean = column_name.replace('_', ' ').lower()
        names.add(clean)
        
        # For compound names
        parts = column_name.split('_')
        if len(parts) > 1:
            names.add(' '.join(parts).lower())
            names.add(parts[-1].lower())
        
        # For names with common patterns
        if 'percentage' in clean:
            names.add(clean.replace('percentage', '%'))
        if 'status' in clean:
            names.add(clean.replace('status', 'state'))
        
        return list(names)
    
    def get_searchable_columns(self, table_name: str) -> Dict[str, str]:
        """
        Get columns that are useful for user queries.
        Excludes IDs and system fields.
        """
        columns = self.get_columns(table_name)
        metadata = self.get_column_metadata(table_name)
        
        # Filter out system columns
        exclude_patterns = ['id', 'uuid', 'pk', '_id', 'created', 'updated', 'timestamp']
        searchable = {}
        
        for col in columns:
            col_lower = col.lower()
            
            # Skip system columns
            if any(pattern in col_lower for pattern in exclude_patterns):
                continue
            
            searchable[col] = metadata[col]
        
        return searchable
    
    def match_query_to_columns(self, table_name: str, user_query: str) -> List[Tuple[str, float]]:
        """
        Find which columns match the user's query.
        Returns list of (column_name, confidence_score) tuples.
        """
        query_lower = user_query.lower()
        searchable = self.get_searchable_columns(table_name)
        
        matches = []
        
        for col_name, col_meta in searchable.items():
            confidence = 0.0
            
            # Check exact word matches
            for natural_name in col_meta['natural_names']:
                if natural_name in query_lower:
                    confidence = max(confidence, 0.9)
                    break
            
            # Check partial matches
            if confidence < 0.9:
                words = query_lower.split()
                for word in words:
                    if len(word) > 3:  # Only match words longer than 3 chars
                        for natural_name in col_meta['natural_names']:
                            if word in natural_name or natural_name in word:
                                confidence = max(confidence, 0.7)
                                break
            
            if confidence > 0.5:
                matches.append((col_name, confidence))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

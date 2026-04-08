"""
Real-Time Dynamic Intent Processor
Loads columns at request time, not startup
Creates intents for EVERY column automatically
"""

import sqlite3
from typing import Dict, List, Tuple, Optional
from functools import lru_cache

class RealTimeDynamicProcessor:
    """
    Process queries dynamically by loading headers at request time.
    Every column in database = Every possible query
    """
    
    def __init__(self, db_path: str, table_name: str, id_column: str):
        self.db_path = db_path
        self.table_name = table_name
        self.id_column = id_column
    
    def get_all_columns(self) -> List[str]:
        """Get all columns from table at request time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    
    def generate_search_terms(self, column_name: str) -> List[str]:
        """Generate all possible search terms for a column"""
        terms = set()
        
        # Original
        terms.add(column_name.lower())
        
        # With underscores removed
        terms.add(column_name.lower().replace('_', ' '))
        
        # Each word separately
        words = column_name.split('_')
        for word in words:
            terms.add(word.lower())
            if len(word) > 3:  # Only meaningful words
                terms.add(word.lower())
        
        # Common abbreviations
        if 'percentage' in column_name.lower():
            terms.add('%')
            terms.add('percent')
            terms.add('pct')
        
        if 'number' in column_name.lower() or 'contact' in column_name.lower():
            terms.add('phone')
            terms.add('call')
            terms.add('mobile')
        
        if 'email' in column_name.lower():
            terms.add('mail')
            terms.add('address')
        
        if 'date' in column_name.lower():
            terms.add('when')
            terms.add('day')
            terms.add('time')
        
        if 'amount' in column_name.lower() or 'fee' in column_name.lower() or 'cost' in column_name.lower():
            terms.add('price')
            terms.add('charge')
            terms.add('expense')
        
        if 'status' in column_name.lower() or 'state' in column_name.lower():
            terms.add('state')
            terms.add('condition')
            terms.add('current')
        
        return list(terms)
    
    def match_column(self, user_query: str) -> Tuple[Optional[str], float]:
        """
        Find the best matching column for user query.
        Returns: (column_name, confidence_score)
        """
        columns = self.get_all_columns()
        query_lower = user_query.lower()
        
        best_match = None
        best_confidence = 0.0
        
        for column in columns:
            # Skip system columns
            if column.lower() in ['id', 'user_id', 'pk', '_id']:
                continue
            
            search_terms = self.generate_search_terms(column)
            
            # Exact match = highest confidence
            for term in search_terms:
                if term == query_lower or (len(term) > 2 and term in query_lower):
                    confidence = 0.95 if term == query_lower else 0.85
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = column
                        break
            
            # Partial match
            if best_confidence < 0.9:
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 3:
                        for term in search_terms:
                            if word in term or term in word:
                                confidence = 0.7
                                if confidence > best_confidence:
                                    best_confidence = confidence
                                    best_match = column
        
        return best_match, best_confidence
    
    def get_record_data(self, identifier: str) -> Optional[Dict]:
        """Get record data for a user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {self.id_column} = ?",
                (identifier,)
            )
            record = cursor.fetchone()
            
            if record:
                return dict(record)
            return None
        finally:
            conn.close()
    
    def process_query(self, user_query: str, record_data: Dict) -> Tuple[str, str, Optional[str]]:
        """
        Process any query by matching to available columns.
        Returns: (response, matched_column, confidence)
        """
        if not record_data:
            return "Sorry, I couldn't fetch your information.", "error", None
        
        # Find matching column
        matched_column, confidence = self.match_column(user_query)
        
        if not matched_column:
            # Show what's available
            all_columns = self.get_all_columns()
            available = [c.replace('_', ' ').title() for c in all_columns if c.lower() not in ['id', 'user_id']]
            
            return f"I can help you with: {', '.join(available[:10])}. What would you like to know?", "help", None
        
        # Get the value
        value = record_data.get(matched_column)
        
        if value is None:
            return f"Sorry, I don't have {matched_column.replace('_', ' ').lower()} information.", matched_column, str(confidence)
        
        # Format response
        display_name = matched_column.replace('_', ' ').title()
        response = f"Your {display_name}: {value}"
        
        return response, matched_column, str(confidence)
    
    def get_all_possible_queries(self) -> Dict[str, List[str]]:
        """
        Get all columns and their possible search terms.
        This shows what queries the user can make.
        """
        columns = self.get_all_columns()
        all_queries = {}
        
        for column in columns:
            if column.lower() in ['id', 'user_id', 'pk', '_id']:
                continue
            
            search_terms = self.generate_search_terms(column)
            all_queries[column] = search_terms
        
        return all_queries
    
    def get_queryable_columns(self) -> List[str]:
        """Get list of all columns user can query"""
        columns = self.get_all_columns()
        return [c for c in columns if c.lower() not in ['id', 'user_id', 'pk', '_id']]
    
    def get_sample_queries(self, limit: int = 10) -> List[str]:
        """Generate sample queries from available columns"""
        columns = self.get_queryable_columns()[:limit]
        queries = []
        
        for col in columns:
            display = col.replace('_', ' ').title()
            # Generate different query formats
            queries.append(f"What's my {display.lower()}?")
            queries.append(f"Show my {display.lower()}")
            if len(queries) >= limit:
                break
        
        return queries[:limit]

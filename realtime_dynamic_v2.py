"""
IMPROVED Real-Time Dynamic Intent Processor - v2
- Semantic similarity for better matching
- Synonym dictionary for accuracy
- Handles 20+ variations of same question
- Works with ANY database columns
"""

import sqlite3
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import re

class RealTimeDynamicProcessor:
    """
    Process queries dynamically with SEMANTIC matching.
    Every column = Every possible query (handles variations automatically)
    """
    
    # Synonym mapping for better matching
    SYNONYMS = {
        'contact': ['phone', 'number', 'mobile', 'call', 'reach', 'telephone', 'cell', 'whatsapp'],
        'email': ['mail', 'email_id', 'address', 'inbox'],
        'name': ['student_name', 'student name', 'full name', 'who'],
        'attendance': ['present', 'attendance_percentage', 'percentage', 'attendance%', 'percentage%'],
        'gpa': ['cgpa', 'grade', 'marks', 'score', 'result', 'grades', 'gpa'],
        'fee': ['fees', 'fees_details', 'cost', 'price', 'charge', 'amount', 'payment', 'tuition'],
        'date': ['birth', 'dob', 'when', 'day', 'born', 'birthday', 'joining'],
        'blood': ['blood_group', 'blood group', 'type', 'rh'],
        'hostel': ['room', 'hostel_room', 'accommodation', 'residence', 'living'],
        'transport': ['transportation', 'travel', 'commute', 'mode', 'vehicle'],
        'internship': ['intern', 'company', 'work', 'placement'],
        'hobby': ['hobbies', 'interest', 'like', 'enjoy'],
        'linkedin': ['linkedin_profile', 'profile', 'social', 'linkedin'],
        'guardian': ['parent', 'father', 'mother', 'emergency', 'contact_person'],
        'nationality': ['country', 'nation', 'origin', 'from'],
        'major': ['branch', 'course', 'program', 'major', 'specialization'],
        'faculty': ['department', 'faculty', 'stream'],
        'status': ['state', 'condition', 'current', 'update'],
    }
    
    def __init__(self, db_path: str, table_name: str, id_column: str):
        self.db_path = db_path
        self.table_name = table_name
        self.id_column = id_column
    
    def get_all_columns(self) -> List[str]:
        """Get all columns from table (real-time discovery)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            return sorted(columns)
        except Exception as e:
            print(f"Error getting columns: {e}")
            return []
    
    def generate_search_terms(self, column_name: str) -> List[str]:
        """Generate comprehensive search terms for a column"""
        terms = set()
        
        # Original formats
        terms.add(column_name.lower())
        terms.add(column_name.lower().replace('_', ' '))
        
        # Split by underscore
        words = column_name.lower().split('_')
        for word in words:
            terms.add(word)
            if len(word) > 2:
                terms.add(word)
        
        # Check synonyms
        for base_word, synonyms in self.SYNONYMS.items():
            if base_word in column_name.lower().replace('_', ' '):
                for syn in synonyms:
                    terms.add(syn)
                    terms.add(syn.replace('_', ' '))
        
        # Add column-specific terms
        col_lower = column_name.lower()
        
        if 'percentage' in col_lower or 'percent' in col_lower:
            terms.update(['%', 'percent', 'pct', 'percentage'])
        
        if 'contact' in col_lower or 'phone' in col_lower or 'mobile' in col_lower:
            terms.update(['phone', 'call', 'reach', 'contact'])
        
        if 'email' in col_lower:
            terms.update(['email', 'mail', 'address'])
        
        if 'date' in col_lower or 'birth' in col_lower or 'joining' in col_lower:
            terms.update(['when', 'date', 'born', 'birthday'])
        
        if 'fee' in col_lower or 'cost' in col_lower or 'amount' in col_lower:
            terms.update(['fee', 'cost', 'price', 'payment', 'amount'])
        
        if 'status' in col_lower or 'state' in col_lower:
            terms.update(['status', 'state', 'current', 'condition'])
        
        if 'blood' in col_lower:
            terms.update(['blood', 'type', 'group', 'rh'])
        
        return [t for t in terms if t and len(t) > 0]
    
    def similarity_score(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0.0 to 1.0)"""
        # Normalize
        s1 = s1.lower().strip()
        s2 = s2.lower().strip()
        
        # Exact match
        if s1 == s2:
            return 1.0
        
        # Use SequenceMatcher for ratio
        ratio = SequenceMatcher(None, s1, s2).ratio()
        return ratio
    
    def match_column(self, user_query: str) -> Tuple[Optional[str], float]:
        """
        Find best matching column using semantic similarity.
        Returns: (column_name, confidence_score)
        
        Handles:
        - Exact matches
        - Synonym matches
        - Partial word matches
        - Semantic similarity
        """
        columns = self.get_all_columns()
        query_lower = user_query.lower()
        
        # Remove question marks and common words
        clean_query = re.sub(r'[?!]', '', query_lower).strip()
        clean_query = clean_query.replace('my ', '').replace('show ', '').replace('what ', '')\
                                 .replace('is ', '').replace('are ', '').replace('can ', '')\
                                 .replace('get ', '').replace('tell ', '').replace('the ', '')
        
        best_match = None
        best_score = 0.0
        
        for column in columns:
            # Skip system columns
            if column.lower() in ['id', 'user_id', 'pk', '_id', 'password', 'hash']:
                continue
            
            col_lower = column.lower().replace('_', ' ')
            search_terms = self.generate_search_terms(column)
            
            # ===== EXACT MATCH (highest) =====
            if clean_query == col_lower or clean_query == column.lower():
                return column, 0.99
            
            # ===== SYNONYM MATCH =====
            for term in search_terms:
                if term == clean_query:
                    score = 0.98
                    if score > best_score:
                        best_score = score
                        best_match = column
            
            # ===== WORD-IN-QUERY MATCH =====
            query_words = clean_query.split()
            for word in query_words:
                if len(word) > 2:
                    for term in search_terms:
                        if word == term:
                            score = 0.95
                            if score > best_score:
                                best_score = score
                                best_match = column
            
            # ===== COLUMN WORD IN QUERY =====
            col_words = col_lower.split()
            for cword in col_words:
                if len(cword) > 3 and cword in clean_query:
                    score = 0.90
                    if score > best_score:
                        best_score = score
                        best_match = column
            
            # ===== SIMILARITY SCORE =====
            col_name = col_lower
            similarity = self.similarity_score(clean_query, col_name)
            
            # Add bonus if any search term matches
            for term in search_terms:
                term_sim = self.similarity_score(clean_query, term)
                if term_sim > 0.7:
                    similarity = max(similarity, term_sim + 0.1)
            
            if similarity > 0.7 and similarity > best_score:
                best_score = similarity
                best_match = column
        
        # If no good match found, try partial matching
        if best_score < 0.7:
            for column in columns:
                if column.lower() in ['id', 'user_id', 'pk', '_id', 'password']:
                    continue
                
                col_lower = column.lower().replace('_', ' ')
                similarity = self.similarity_score(clean_query, col_lower)
                
                if similarity > best_score and similarity > 0.5:
                    best_score = similarity
                    best_match = column
        
        return best_match, best_score
    
    def get_record_data(self, identifier: str) -> Optional[Dict]:
        """Get record data for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {self.id_column} = ?",
                (identifier,)
            )
            record = cursor.fetchone()
            
            if record:
                return dict(record)
            return None
        except Exception as e:
            print(f"Error fetching record: {e}")
            return None
        finally:
            conn.close()
    
    def process_query(self, user_query: str, record_data: Dict) -> Tuple[str, str, str]:
        """
        Process query with semantic matching.
        Returns: (response, matched_column, confidence)
        """
        if not record_data:
            return "Sorry, I couldn't fetch your information.", "error", "0.0"
        
        # Find matching column
        matched_column, confidence = self.match_column(user_query)
        
        if not matched_column or confidence < 0.5:
            # Show available columns
            all_columns = self.get_all_columns()
            available = [c.replace('_', ' ').title() for c in all_columns 
                        if c.lower() not in ['id', 'user_id', 'pk', '_id', 'password']]
            
            return (f"I can help with: {', '.join(available[:8])}. What would you like to know?", 
                   "help", "0.0")
        
        # Get the value
        value = record_data.get(matched_column)
        
        if value is None or value == '':
            display_name = matched_column.replace('_', ' ').title()
            return (f"Sorry, I don't have {display_name.lower()} information yet.", 
                   matched_column, f"{confidence:.2f}")
        
        # Format response
        display_name = matched_column.replace('_', ' ').title()
        response = f"Your {display_name}: {value}"
        
        return response, matched_column, f"{confidence:.2f}"
    
    def get_all_possible_queries(self) -> Dict[str, List[str]]:
        """Get all columns and their search terms"""
        columns = self.get_all_columns()
        all_queries = {}
        
        for column in columns:
            if column.lower() in ['id', 'user_id', 'pk', '_id', 'password']:
                continue
            
            search_terms = self.generate_search_terms(column)
            all_queries[column] = list(set(search_terms))  # Remove duplicates
        
        return all_queries
    
    def get_queryable_columns(self) -> List[str]:
        """Get all columns user can query"""
        columns = self.get_all_columns()
        return [c for c in columns 
               if c.lower() not in ['id', 'user_id', 'pk', '_id', 'password']]
    
    def get_sample_queries(self, limit: int = 10) -> List[str]:
        """Generate diverse sample queries"""
        columns = self.get_queryable_columns()[:limit]
        queries = []
        
        templates = [
            "What's my {col}?",
            "Show my {col}",
            "Tell me my {col}",
            "Get my {col}",
            "My {col} is?",
            "Can you get my {col}?",
        ]
        
        template_idx = 0
        for col in columns:
            display = col.replace('_', ' ').lower()
            template = templates[template_idx % len(templates)]
            queries.append(template.format(col=display))
            template_idx += 1
            
            if len(queries) >= limit:
                break
        
        return queries[:limit]

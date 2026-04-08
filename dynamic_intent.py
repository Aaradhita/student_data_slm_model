"""
Dynamic Intent Processor
Generates intents and responses based on available schema
"""

import sqlite3
from typing import Dict, List, Tuple, Optional
from schema_discovery import SchemaDiscovery

class DynamicIntentProcessor:
    """Process user queries dynamically based on available columns"""
    
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name
        self.schema = SchemaDiscovery(db_path)
        self.columns_metadata = self.schema.get_column_metadata(table_name)
        self.searchable_columns = self.schema.get_searchable_columns(table_name)
    
    def get_available_intents(self) -> Dict[str, str]:
        """
        Get all available intents based on columns.
        Maps intent_name -> display_description
        """
        intents = {}
        
        for col_name, meta in self.searchable_columns.items():
            intent_name = col_name.lower().replace(' ', '_')
            intents[intent_name] = meta['display_name']
        
        return intents
    
    def process_query(self, user_query: str, record_data: Dict) -> Tuple[str, str, Optional[List[Dict]]]:
        """
        Process user query and generate response.
        Returns: (response_text, intent, matched_columns)
        """
        query_lower = user_query.lower()
        
        # Find matching columns
        matches = self.schema.match_query_to_columns(self.table_name, user_query)
        
        if not matches:
            return self._generate_help_response(), "unknown", None
        
        # Get top match
        matched_column, confidence = matches[0]
        
        # Get the value from the record
        value = record_data.get(matched_column)
        
        if value is None:
            return f"Sorry, I don't have {self.columns_metadata[matched_column]['display_name'].lower()} information.", matched_column, None
        
        # Generate response based on column type
        response = self._format_response(matched_column, value, record_data, matches[:3])
        
        return response, matched_column, matches
    
    def _format_response(self, column_name: str, value: any, record_data: Dict, related_matches: List) -> str:
        """Format the response based on column type and value"""
        meta = self.columns_metadata[column_name]
        col_type = meta['type']
        display_name = meta['display_name']
        
        # Format value based on type
        if col_type == 'numeric':
            if isinstance(value, str):
                try:
                    value = float(value)
                except:
                    pass
            if isinstance(value, (int, float)):
                # Check if it looks like a score/GPA
                if any(word in column_name.lower() for word in ['gpa', 'cgpa', 'score', 'marks']):
                    response = f"Your {display_name}: {value}"
                    # Try to add related info
                    if len(related_matches) > 1:
                        for rel_col, _ in related_matches[1:]:
                            rel_value = record_data.get(rel_col)
                            if rel_value:
                                response += f". {self.columns_metadata[rel_col]['display_name']}: {rel_value}"
                                break
                    return response
        
        elif col_type == 'percentage':
            response = f"Your {display_name}: {value}"
        
        elif col_type == 'status':
            response = f"Your {display_name}: {value}"
            # Add related info if available
            if len(related_matches) > 1:
                for rel_col, _ in related_matches[1:]:
                    rel_value = record_data.get(rel_col)
                    if rel_value and self.columns_metadata[rel_col]['type'] in ['numeric', 'text']:
                        response += f". {self.columns_metadata[rel_col]['display_name']}: {rel_value}"
                        break
        
        elif col_type == 'contact':
            response = f"Your {display_name}: {value}"
        
        elif col_type == 'date':
            response = f"Your {display_name}: {value}"
        
        else:  # TEXT or UNKNOWN
            response = f"Your {display_name}: {value}"
        
        return response
    
    def _generate_help_response(self) -> str:
        """Generate a help message with available fields"""
        intents = self.get_available_intents()
        
        if not intents:
            return "I can help you with your information. What would you like to know?"
        
        # Get first 5-7 columns to show
        sample_intents = list(intents.values())[:7]
        
        response = "I can help you with: " + ", ".join(sample_intents) + ", and more. What would you like to know?"
        return response
    
    def get_record_data(self, register_number: str) -> Optional[Dict]:
        """
        Get record data for a user by their identifier.
        Tries to find primary identifier automatically.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Try to find identifier column
            columns = self.schema.get_columns(self.table_name)
            
            # Look for common identifier columns
            id_columns = [col for col in columns if any(
                pattern in col.lower() for pattern in ['register', 'id', 'code', 'number', 'student_id']
            )]
            
            if id_columns:
                id_col = id_columns[0]
                cursor.execute(
                    f"SELECT * FROM {self.table_name} WHERE {id_col} = ?",
                    (register_number,)
                )
            else:
                # Fallback to first column as identifier
                cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
            
            record = cursor.fetchone()
            
            if record:
                return dict(record)
            return None
            
        finally:
            conn.close()
    
    def print_schema_info(self):
        """Print available schema information (useful for debugging)"""
        print("\n" + "="*60)
        print(f"Dataset: {self.table_name}")
        print("="*60)
        print("\nAvailable Columns:")
        
        for col_name, meta in self.searchable_columns.items():
            print(f"  • {meta['display_name']}")
            print(f"    Type: {meta['type']}")
            print(f"    Search as: {', '.join(meta['natural_names'][:3])}")
            print()
        
        print("="*60)
        print("\nExample Queries:")
        intents = self.get_available_intents()
        for i, (intent, display) in enumerate(list(intents.items())[:5], 1):
            print(f"  {i}. \"What's my {display.lower()}?\"")
        print()

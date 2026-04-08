"""
Test the IMPROVED matching system with 20+ variations
"""

from realtime_dynamic_v2 import RealTimeDynamicProcessor
from config import ACTIVE_CONFIG

processor = RealTimeDynamicProcessor(
    ACTIVE_CONFIG.DATABASE_PATH,
    ACTIVE_CONFIG.DATA_TABLE,
    ACTIVE_CONFIG.USER_ID_COLUMN
)

# Get test data
record_data = processor.get_record_data('REG1000')

# Test variations - same intent, different wording
test_queries = {
    'CGPA': [
        'What is my CGPA?',
        'Show my GPA',
        'What is my grade?',
        'My score?',
        'What are my marks?',
        'Tell me my grade',
        'Can you get my marks?',
        'How is my performance?',
        'My CGPA please',
        'Show my academic score',
        'What is my grade point?',
        'Get my GPA',
    ],
    'Contact_Number': [
        'What is my contact number?',
        'Show my phone',
        'Phone number?',
        'How to reach me?',
        'My mobile?',
        'Contact please',
        'Tell me my number',
        'Get my phone',
        'What is my mobile?',
        'My contact?',
        'Show my cell number',
        'Can you get my phone?',
    ],
    'Blood_Group': [
        'What is my blood group?',
        'My blood type?',
        'Show blood group',
        'Blood group please',
        'What is my blood type?',
        'My type?',
        'Blood group',
        'Tell me my type',
        'What blood type am I?',
        'Blood?',
    ],
    'Internship_Status': [
        'Where am I interning?',
        'Internship status?',
        'Where is my internship?',
        'Show my internship',
        'My internship details?',
        'Internship?',
        'Where do I work?',
        'Placement status?',
        'Is there an internship?',
        'Tell me about my placement',
    ],
    'Hobbies': [
        'What are my hobbies?',
        'Show my interests',
        'What do I like?',
        'My hobbies?',
        'What are my interests?',
        'Tell me my hobbies',
        'What do I enjoy?',
        'My favorite activities?',
        'What interests me?',
    ],
}

print("=" * 80)
print("IMPROVED MATCHING SYSTEM - ACCURACY TEST")
print("=" * 80)
print(f"\nTest Data: Register {record_data[ACTIVE_CONFIG.USER_ID_COLUMN]}")

for column, queries in test_queries.items():
    print(f"\n{'=' * 80}")
    print(f"📌 Testing Column: {column}")
    print(f"{'=' * 80}")
    
    correct_matches = 0
    
    for query in queries:
        matched_col, confidence = processor.match_column(query)
        
        is_correct = matched_col == column
        status = "✓" if is_correct else "✗"
        
        if is_correct:
            correct_matches += 1
        
        print(f"{status} Q: {query:<40} → {matched_col} (confidence: {confidence:.2f})")
    
    accuracy = (correct_matches / len(queries)) * 100
    print(f"\n   Accuracy for {column}: {correct_matches}/{len(queries)} ({accuracy:.1f}%)")

# Test with new columns
print(f"\n{'=' * 80}")
print("🆕 AUTO-DISCOVERY TEST (New Columns Added to Excel)")
print(f"{'=' * 80}")

all_columns = processor.get_all_columns()
print(f"\nTotal columns auto-discovered: {len(all_columns)}")
print(f"Columns: {', '.join(all_columns)}")

print(f"\n{'=' * 80}")
print("✅ IMPROVED System Ready!")
print(f"{'=' * 80}")

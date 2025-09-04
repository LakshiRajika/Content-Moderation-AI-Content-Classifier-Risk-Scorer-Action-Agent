import json
import pandas as pd
from datetime import datetime
import hashlib

class FeedbackSystem:
    def __init__(self, feedback_file="feedback_data.csv"):
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self):
        """Load feedback data from file"""
        try:
            return pd.read_csv(self.feedback_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'timestamp', 'content_hash', 'user_id', 'accurate', 
                'notes', 'expected_classification', 'expected_action'
            ])
    
    def record_feedback(self, content, user_id, accurate, notes="", 
                       expected_classification=None, expected_action=None):
        """Record user feedback about moderation accuracy"""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'user_id': user_id,
            'accurate': accurate,
            'notes': notes,
            'expected_classification': json.dumps(expected_classification) if expected_classification else None,
            'expected_action': json.dumps(expected_action) if expected_action else None
        }
        
        # Add to DataFrame
        new_df = pd.DataFrame([feedback_entry])
        self.feedback_data = pd.concat([self.feedback_data, new_df], ignore_index=True)
        self._save_feedback()
        
        return True
    
    def _save_feedback(self):
        """Save feedback data to file"""
        self.feedback_data.to_csv(self.feedback_file, index=False)
    
    def get_feedback_stats(self):
        """Calculate accuracy metrics from feedback"""
        if self.feedback_data.empty:
            return {
                'total_feedback': 0,
                'accuracy_percentage': 0,
                'accuracy_count': 0,
                'inaccuracy_count': 0
            }
        
        accurate_count = len(self.feedback_data[self.feedback_data['accurate'] == True])
        total_feedback = len(self.feedback_data)
        
        return {
            'total_feedback': total_feedback,
            'accuracy_percentage': (accurate_count / total_feedback * 100) if total_feedback > 0 else 0,
            'accuracy_count': accurate_count,
            'inaccuracy_count': total_feedback - accurate_count
        }
    
    def export_training_data(self):
        """
        Prepare misclassified examples for model retraining
        Returns examples where users indicated inaccuracies
        """
        if self.feedback_data.empty:
            return []
        
        # Get inaccurate classifications with expected outcomes
        inaccurate_feedback = self.feedback_data[
            (self.feedback_data['accurate'] == False) &
            (self.feedback_data['expected_classification'].notna())
        ]
        
        training_examples = []
        for _, row in inaccurate_feedback.iterrows():
            example = {
                'content_hash': row['content_hash'],
                'expected_classification': json.loads(row['expected_classification']),
                'notes': row['notes']
            }
            
            if pd.notna(row['expected_action']):
                example['expected_action'] = json.loads(row['expected_action'])
            
            training_examples.append(example)
        
        return training_examples
    
    def get_recent_feedback(self, limit=10):
        """Get most recent feedback entries"""
        if self.feedback_data.empty:
            return []
        
        recent = self.feedback_data.sort_values('timestamp', ascending=False).head(limit)
        return recent.to_dict('records')
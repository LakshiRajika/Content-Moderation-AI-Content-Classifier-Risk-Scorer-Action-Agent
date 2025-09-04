import pandas as pd
import json
from datetime import datetime

class DatasetManager:
    def __init__(self, dataset_path="moderation_dataset.csv"):
        self.dataset_path = dataset_path
        self.dataset = self._load_dataset()
    
    def _load_dataset(self):
        """Load or create moderation dataset"""
        try:
            return pd.read_csv(self.dataset_path)
        except FileNotFoundError:
            # Create new dataset with columns
            return pd.DataFrame(columns=[
                'timestamp', 'content_hash', 'user_id', 'classification', 
                'risk_score', 'action_taken'
            ])
    
    def add_to_dataset(self, content, user_id, classification, risk_score, action):
        """Add moderation decision to dataset for training"""
        new_entry = {
            'timestamp': datetime.now().isoformat(),
            'content_hash': hash(content),
            'user_id': user_id,
            'classification': json.dumps(classification),
            'risk_score': json.dumps(risk_score),
            'action_taken': json.dumps(action)
        }
        
        # Convert to DataFrame and append
        new_df = pd.DataFrame([new_entry])
        self.dataset = pd.concat([self.dataset, new_df], ignore_index=True)
        self._save_dataset()
        return True
    
    def _save_dataset(self):
        """Save dataset to CSV"""
        self.dataset.to_csv(self.dataset_path, index=False)
    
    def get_dataset_stats(self):
        """Get statistics about the collected dataset"""
        return {
            "total_entries": len(self.dataset),
            "last_entry": self.dataset['timestamp'].max() if not self.dataset.empty else "No entries"
        }

# Test the dataset manager
if __name__ == "__main__":
    dm = DatasetManager()
    print("Dataset manager created successfully!")
    print("Stats:", dm.get_dataset_stats())
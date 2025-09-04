import json
import pandas as pd
from datetime import datetime, timedelta

class RetrievalAgent:
    def __init__(self, dataset_manager):
        self.dataset_manager = dataset_manager
    
    def search_similar_content(self, current_classification, threshold=0.6):
        """
        Simple version - find similar content based on classification patterns
        """
        if self.dataset_manager.dataset.empty:
            return []
        
        similar_cases = []
        
        try:
            for _, row in self.dataset_manager.dataset.iterrows():
                try:
                    # Get historical classification
                    hist_classification = json.loads(row['classification'])
                    
                    # Calculate simple similarity score
                    similarity_score = 0
                    matching_categories = 0
                    
                    for category, current_score in current_classification.items():
                        if category in hist_classification:
                            hist_score = hist_classification[category]
                            # Ensure both are numbers
                            if isinstance(current_score, (int, float)) and isinstance(hist_score, (int, float)):
                                similarity_score += min(current_score, hist_score)
                                matching_categories += 1
                    
                    # Calculate average similarity
                    if matching_categories > 0:
                        similarity_score /= matching_categories
                    
                    # Add to results if above threshold
                    if similarity_score >= threshold:
                        similar_cases.append({
                            'similarity': similarity_score,
                            'classification': hist_classification,
                            'risk_score': json.loads(row['risk_score']),
                            'action_taken': json.loads(row['action_taken']),
                            'timestamp': str(row['timestamp'])
                        })
                
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error processing row: {e}")
                    continue
            
            # Sort by similarity (highest first)
            similar_cases.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_cases[:5]  # Return top 5 similar cases
            
        except Exception as e:
            print(f"Error in search_similar_content: {e}")
            return []  # Return empty list instead of crashing
    
    def retrieve_precedents(self, classification, min_confidence=0.5):
        """
        Simple version - retrieve historical precedents
        """
        precedents = []
        
        if self.dataset_manager.dataset.empty:
            return precedents
        
        # Filter for significant classifications
        for _, row in self.dataset_manager.dataset.iterrows():
            try:
                hist_classification = json.loads(row['classification'])
                
                # Check if any classification category meets minimum confidence
                matching_categories = []
                for category, confidence in classification.items():
                    # Ensure both values are numbers
                    hist_confidence = hist_classification.get(category, 0)
                    if (isinstance(hist_confidence, (int, float)) and 
                        isinstance(confidence, (int, float)) and
                        float(hist_confidence) >= min_confidence and
                        float(confidence) >= min_confidence):
                        matching_categories.append(category)
                
                if matching_categories:
                    precedents.append({
                        'matching_categories': matching_categories,
                        'classification': hist_classification,
                        'risk_score': json.loads(row['risk_score']),
                        'action_taken': json.loads(row['action_taken']),
                        'timestamp': str(row['timestamp'])
                    })
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error processing row: {e}")
                continue
        
        return precedents
    
    def get_trend_analysis(self, days=30):
        """
        Simple trend analysis
        """
        if self.dataset_manager.dataset.empty:
            return {}
        
        try:
            # Filter recent data
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = self.dataset_manager.dataset[
                pd.to_datetime(self.dataset_manager.dataset['timestamp']) >= cutoff_date
            ]
        except (ValueError, KeyError):
            return {}
        
        if recent_data.empty:
            return {}
        
        # Calculate statistics
        trend_analysis = {
            'total_moderations': len(recent_data),
            'high_risk_count': 0,
            'common_categories': {},
            'average_risk_score': 0
        }
        
        risk_scores = []
        for _, row in recent_data.iterrows():
            try:
                risk_data = json.loads(row['risk_score'])
                classification = json.loads(row['classification'])
                
                if risk_data.get('level') == 'High':
                    trend_analysis['high_risk_count'] += 1
                
                # Ensure risk score is a number
                risk_score = risk_data.get('score', 0)
                if isinstance(risk_score, (int, float)):
                    risk_scores.append(float(risk_score))
                
                # Count category occurrences
                for category, score in classification.items():
                    if isinstance(score, (int, float)) and float(score) > 0.5:
                        trend_analysis['common_categories'][category] = trend_analysis['common_categories'].get(category, 0) + 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        if risk_scores:
            trend_analysis['average_risk_score'] = sum(risk_scores) / len(risk_scores)
        
        return trend_analysis
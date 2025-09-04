from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
import re
from typing import Dict

class ClassifierAgent:
    def __init__(self):
        self.categories = [
            "hate speech", "harassment", "violence", "self-harm",
            "sexual content", "spam", "misinformation"
        ]
        
        try:
            # Try to use a model better suited for content moderation
            print("Loading classification model...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Use CPU
            )
            self.model_loaded = True
            print("✅ Classification model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading classification model: {e}")
            self.model_loaded = False
            self.classifier = None
    
    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify text into content moderation categories
        Returns a dictionary of category: confidence_score
        """
        # First, apply rule-based filters
        if self._contains_url(text):
            return self._create_classification_result({"spam": 0.8})
        
        if self._is_all_caps(text) and len(text) > 15:
            return self._create_classification_result({"harassment": 0.6, "spam": 0.5})
        
        # If model failed to load or text is very short, use rule-based
        if not self.model_loaded or len(text.strip()) < 5:
            return self._rule_based_classification(text)
        
        try:
            # Use the model for classification
            result = self.classifier(
                text,
                candidate_labels=self.categories,
                multi_label=True,
                hypothesis_template="This text contains {}."  # Better template for content moderation
            )
            
            # Process the results
            classification = {}
            for label, score in zip(result['labels'], result['scores']):
                classification[label] = float(score)
            
            # Apply minimum confidence threshold
            classification = {k: v for k, v in classification.items() if v > 0.1}
            
            # If no categories detected above threshold, consider it normal
            if not classification:
                return self._create_classification_result({})
            
            return self._create_classification_result(classification)
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return self._rule_based_classification(text)
    
    def _create_classification_result(self, detected_categories: Dict[str, float]) -> Dict[str, float]:
        """
        Create a proper classification result with normalized probabilities
        """
        result = {}
        
        # Add detected categories
        for category, score in detected_categories.items():
            result[category] = score
        
        # Calculate normal content probability
        abnormal_score = sum(detected_categories.values())
        normal_score = max(0.1, 1.0 - abnormal_score)  # Ensure at least 10% normal
        
        # Normalize to make sum approximately 100%
        total = sum(result.values()) + normal_score
        if total > 0:
            for category in result:
                result[category] /= total
            result["normal content"] = normal_score / total
        else:
            result["normal content"] = 1.0
        
        return result
    
    def _rule_based_classification(self, text: str) -> Dict[str, float]:
        """Fallback to rule-based classification when model fails"""
        text_lower = text.lower()
        detected_categories = {}
        
        # Hate speech detection
        hate_words = ["hate", "stupid", "idiot", "retard", "kill all", "die"]
        if any(word in text_lower for word in hate_words):
            detected_categories["hate speech"] = 0.7
        
        # Violence detection
        violence_words = ["kill", "hurt", "violence", "attack", "fight", "punch"]
        if any(word in text_lower for word in violence_words):
            detected_categories["violence"] = 0.6
        
        # Sexual content detection
        sexual_words = ["sex", "nude", "naked", "porn", "xxx", "adult"]
        if any(word in text_lower for word in sexual_words):
            detected_categories["sexual content"] = 0.5
        
        # Spam detection
        spam_words = ["free", "offer", "win", "prize", "click", "buy now"]
        if any(word in text_lower for word in spam_words):
            detected_categories["spam"] = 0.4
        
        return self._create_classification_result(detected_categories)
    
    def _contains_url(self, text: str) -> bool:
        """Check if text contains URLs"""
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return bool(url_pattern.search(text))
    
    def _is_all_caps(self, text: str) -> bool:
        """Check if text is all uppercase (often indicates shouting)"""
        return text.upper() == text and len(text) > 5
class RiskAgent:
    def __init__(self):
        self.thresholds = {
            "hate speech": 0.4,  # Lowered thresholds to be more sensitive
            "harassment": 0.4,
            "violence": 0.3,     # Violence should be very sensitive
            "self-harm": 0.3,
            "sexual content": 0.4,
            "spam": 0.6,
            "misinformation": 0.5
        }
    
    def evaluate_risk(self, classification, text):
        print(f"🔍 Risk evaluation for: {classification}")  # DEBUG
        risk_score = 0.0
        reasons = []
        
        # Calculate risk based on classification scores
        for category, score in classification.items():
            if category == "normal content":
                continue  # Skip normal content
                
            numeric_score = self._ensure_float(score)
            threshold = self.thresholds.get(category, 0.4)
            
            print(f"   {category}: {numeric_score} vs threshold {threshold}")  # DEBUG
            
            if numeric_score > threshold:
                contribution = numeric_score * self._get_category_weight(category)
                risk_score += contribution
                reasons.append(f"High {category} probability: {numeric_score:.2f}")
                print(f"   ✅ {category} contributes {contribution:.2f} to risk")  # DEBUG
        
        # Additional risk factors from text characteristics
        text_risk = self._evaluate_text_characteristics(text)
        risk_score += text_risk
        print(f"   Text characteristics add {text_risk:.2f} risk")  # DEBUG
        
        # Ensure minimum risk for certain keywords
        risk_score = self._apply_keyword_boost(text, risk_score)
        
        # Normalize to 0-1 range
        risk_score = min(1.0, max(0.0, risk_score))  # Clamp between 0 and 1
        print(f"   Final risk score: {risk_score:.2f}")  # DEBUG
        
        return {
            "score": risk_score,
            "reasons": reasons,
            "level": self._get_risk_level(risk_score)
        }
    
    def _ensure_float(self, value):
        """Convert value to float if it's a string, otherwise return as is"""
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return 0.0
    
    def _get_category_weight(self, category):
        weights = {
            "violence": 0.7,      # Much higher weight for violence
            "self-harm": 0.7,     # Much higher weight for self-harm
            "sexual content": 0.6,  # Increased from 0.25 to 0.6
            "hate speech": 0.5,
            "harassment": 0.5,
            "spam": 0.2,
            "misinformation": 0.3
        }
        return weights.get(category, 0.3)
    
    def _evaluate_text_characteristics(self, text):
        risk = 0.0
        # Threatening language gets extra risk
        if any(word in text.lower() for word in ["kill", "hurt", "die", "harm", "attack"]):
            risk += 0.3
            
        # Sexual content language gets extra risk
        if any(word in text.lower() for word in ["nude", "naked", "show me", "send", "pics", "photos", "private"]):
            risk += 0.4
            
        if len(text) > 200:  # Long texts
            risk += 0.1
        if text.count('!') > 2:  # Multiple exclamation points
            risk += 0.1
        if text.upper() == text and len(text) > 10:  # ALL CAPS
            risk += 0.2
        return risk
    
    def _apply_keyword_boost(self, text, current_risk):
        """Apply minimum risk scores for clearly dangerous content"""
        text_lower = text.lower()
        
        # Extreme violence threats
        if any(word in text_lower for word in ["kill you", "kill myself", "want to die", "suicide"]):
            return max(current_risk, 0.8)  # At least 80% risk
            
        # Direct threats
        if any(word in text_lower for word in ["kill", "murder", "hurt you", "attack you"]):
            return max(current_risk, 0.7)  # At least 70% risk
        
        # Sexual content requests - NEW
        if any(word in text_lower for word in ["nude", "naked", "show me", "send pics", "sexual", "private parts"]):
            return max(current_risk, 0.5)  # At least 50% risk for sexual requests
        
        # Inappropriate requests - NEW
        if any(word in text_lower for word in ["can you show", "can you send", "want to see", "show your"]):
            if any(sexual_word in text_lower for sexual_word in ["nude", "naked", "private", "body", "photos"]):
                return max(current_risk, 0.6)  # At least 60% risk
            
        return current_risk
    
    def _get_risk_level(self, score):
        if score < 0.3:
            return "Low"
        elif score < 0.7:
            return "Medium"
        else:
            return "High"
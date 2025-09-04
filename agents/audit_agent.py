import json
from datetime import datetime
import hashlib
import os

class AuditAgent:
    def __init__(self, log_file="audit_log.json"):
        self.log_file = log_file
        self.audit_log = self._load_audit_log()
    
    def _load_audit_log(self):
        """Load existing audit log from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_audit_log(self):
        """Save audit log to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
        except Exception as e:
            print(f"Error saving audit log: {e}")
    
    def log_decision(self, content, user_id, classification, risk_score, action, explanation):
        """Log moderation decision for transparency"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "user_id": user_id,
            "classification": classification,
            "risk_score": risk_score,
            "action_taken": action,
            "explanation": explanation
        }
        
        self.audit_log.append(audit_entry)
        self._save_audit_log()
        return audit_entry
    
    def generate_explanation(self, classification, risk_score):
        """Generate human-readable explanation for decisions"""
        explanations = []
        
        # Explain classifications
        for category, score in classification.items():
            if score > 0.3:  # Only explain significant classifications
                explanations.append(f"Detected {category} ({score:.0%} confidence)")
        
        # Explain risk factors
        if risk_score.get('reasons'):
            explanations.append("Risk factors: " + ", ".join(risk_score['reasons']))
        
        # Explain risk level
        risk_level = risk_score.get('level', 'Unknown')
        risk_value = risk_score.get('score', 0)
        explanations.append(f"Overall risk level: {risk_level} ({risk_value:.0%})")
        
        return ". ".join(explanations)
    
    def get_audit_stats(self):
        """Generate statistics for responsible AI reporting"""
        if not self.audit_log:
            return {
                "total_decisions": 0, 
                "high_risk_percentage": 0,
                "medium_risk_percentage": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0
            }
        
        total = len(self.audit_log)
        high_risk_count = 0
        medium_risk_count = 0
        
        for entry in self.audit_log:
            risk_level = entry.get('risk_score', {}).get('level', '')
            if risk_level == 'High':
                high_risk_count += 1
            elif risk_level == 'Medium':
                medium_risk_count += 1
        
        high_risk_percentage = (high_risk_count / total * 100) if total > 0 else 0
        medium_risk_percentage = (medium_risk_count / total * 100) if total > 0 else 0
        
        return {
            "total_decisions": total,
            "high_risk_percentage": round(high_risk_percentage, 1),
            "medium_risk_percentage": round(medium_risk_percentage, 1),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count
        }

# Test the audit agent
if __name__ == "__main__":
    auditor = AuditAgent()
    print("Audit agent created successfully!")
    print("Initial stats:", auditor.get_audit_stats())
class ActionAgent:
    def __init__(self):
        self.action_policies = {
            "Low": ["no action", "allow content"],
            "Medium": ["flag for review", "notify moderator", "add content warning"],
            "High": ["remove content", "notify administrator", "temporary ban user", "report to authorities"]
        }
    
    def determine_action(self, risk_assessment, classification, text):
        risk_level = risk_assessment["level"]
        
        # Base actions on risk level
        actions = self.action_policies.get(risk_level, ["review manually"])
        
        # Customize actions based on specific classifications
        if classification.get("self-harm", 0) > 0.6:
            actions.append("provide mental health resources")
        
        if classification.get("violence", 0) > 0.7:
            actions.append("report to authorities if credible threat")
            
        # NEW: Specific actions for sexual content
        if classification.get("sexual content", 0) > 0.5:
            if risk_level == "Medium":
                actions.extend(["add content warning", "review by human moderator"])
            elif risk_level == "High":
                actions.extend(["remove content immediately", "notify platform safety team"])
        
        # NEW: Additional checks for explicit sexual requests
        text_lower = text.lower()
        if any(word in text_lower for word in ["nude", "naked", "send pics", "show me"]) and classification.get("sexual content", 0) > 0.4:
            actions.append("escalate to senior moderator")
        
        return {
            "actions": actions,
            "explanation": f"Risk level: {risk_level} ({risk_assessment['score']:.2f})"
        }
#!/usr/bin/env python3
"""
Quick verification that all system components are working
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.classifier_agent import ClassifierAgent
from agents.risk_agent import RiskAgent
from agents.action_agent import ActionAgent
from agents.audit_agent import AuditAgent
from agents.retrieval_agent import RetrievalAgent
from utils.dataset_manager import DatasetManager
from utils.feedback_system import FeedbackSystem

def test_classifier():
    """Test the ClassifierAgent"""
    print("🧪 Testing ClassifierAgent...")
    try:
        classifier = ClassifierAgent()
        test_text = "This is some test content with violence"
        classification = classifier.classify(test_text)
        print(f"   Input: '{test_text}'")
        print(f"   Classification: {classification}")
        print("   ✅ ClassifierAgent working")
        return True
    except Exception as e:
        print(f"   ❌ ClassifierAgent failed: {e}")
        return False

def test_risk_agent():
    """Test the RiskAgent"""
    print("🧪 Testing RiskAgent...")
    try:
        risk_agent = RiskAgent()
        test_classification = {"violence": 0.8, "normal content": 0.2}
        test_text = "I will hurt someone"
        risk_assessment = risk_agent.evaluate_risk(test_classification, test_text)
        print(f"   Classification: {test_classification}")
        print(f"   Risk Assessment: {risk_assessment}")
        print("   ✅ RiskAgent working")
        return True
    except Exception as e:
        print(f"   ❌ RiskAgent failed: {e}")
        return False

def test_action_agent():
    """Test the ActionAgent"""
    print("🧪 Testing ActionAgent...")
    try:
        action_agent = ActionAgent()
        test_risk = {"score": 0.8, "level": "High", "reasons": ["High violence probability"]}
        test_classification = {"violence": 0.8}
        test_text = "Violent content"
        actions = action_agent.determine_action(test_risk, test_classification, test_text)
        print(f"   Risk: {test_risk}")
        print(f"   Actions: {actions}")
        print("   ✅ ActionAgent working")
        return True
    except Exception as e:
        print(f"   ❌ ActionAgent failed: {e}")
        return False

def test_audit_agent():
    """Test the AuditAgent"""
    print("🧪 Testing AuditAgent...")
    try:
        audit_agent = AuditAgent("test_audit_log.json")
        test_classification = {"violence": 0.8}
        test_risk = {"score": 0.8, "level": "High"}
        explanation = audit_agent.generate_explanation(test_classification, test_risk)
        audit_entry = audit_agent.log_decision(
            "Test content", "test_user", test_classification, 
            test_risk, ["remove content"], explanation
        )
        print(f"   Explanation: {explanation}")
        print(f"   Audit entry created: {bool(audit_entry)}")
        stats = audit_agent.get_audit_stats()
        print(f"   Audit stats: {stats}")
        
        # Clean up test file
        if os.path.exists("test_audit_log.json"):
            os.remove("test_audit_log.json")
            
        print("   ✅ AuditAgent working")
        return True
    except Exception as e:
        print(f"   ❌ AuditAgent failed: {e}")
        return False

def test_dataset_manager():
    """Test the DatasetManager"""
    print("🧪 Testing DatasetManager...")
    try:
        dataset_manager = DatasetManager("test_dataset.csv")
        stats = dataset_manager.get_dataset_stats()
        print(f"   Initial stats: {stats}")
        
        # Add test entry
        success = dataset_manager.add_to_dataset(
            "Test content", "test_user", 
            {"violence": 0.8}, {"score": 0.8}, ["remove content"]
        )
        print(f"   Entry added: {success}")
        
        stats = dataset_manager.get_dataset_stats()
        print(f"   Updated stats: {stats}")
        
        # Clean up test file
        if os.path.exists("test_dataset.csv"):
            os.remove("test_dataset.csv")
            
        print("   ✅ DatasetManager working")
        return True
    except Exception as e:
        print(f"   ❌ DatasetManager failed: {e}")
        return False

def test_retrieval_agent():
    """Test the RetrievalAgent"""
    print("🧪 Testing RetrievalAgent...")
    try:
        # First create a test dataset
        dataset_manager = DatasetManager("test_dataset.csv")
        dataset_manager.add_to_dataset(
            "Violent content here", "user1", 
            {"violence": 0.9, "hate speech": 0.3}, 
            {"score": 0.85, "level": "High"}, 
            ["remove content", "notify admin"]
        )
        
        retrieval_agent = RetrievalAgent(dataset_manager)
        test_classification = {"violence": 0.8, "normal content": 0.2}
        similar_cases = retrieval_agent.search_similar_content(test_classification)
        print(f"   Similar cases found: {len(similar_cases)}")
        
        # Clean up test file
        if os.path.exists("test_dataset.csv"):
            os.remove("test_dataset.csv")
            
        print("   ✅ RetrievalAgent working")
        return True
    except Exception as e:
        print(f"   ❌ RetrievalAgent failed: {e}")
        return False

def test_feedback_system():
    """Test the FeedbackSystem"""
    print("🧪 Testing FeedbackSystem...")
    try:
        feedback_system = FeedbackSystem("test_feedback.csv")
        success = feedback_system.record_feedback(
            "Test content", "test_user", True, "Test feedback"
        )
        print(f"   Feedback recorded: {success}")
        
        stats = feedback_system.get_feedback_stats()
        print(f"   Feedback stats: {stats}")
        
        training_data = feedback_system.export_training_data()
        print(f"   Training data entries: {len(training_data)}")
        
        # Clean up test file
        if os.path.exists("test_feedback.csv"):
            os.remove("test_feedback.csv")
            
        print("   ✅ FeedbackSystem working")
        return True
    except Exception as e:
        print(f"   ❌ FeedbackSystem failed: {e}")
        return False

def main():
    print("🔍 Starting System Verification...")
    print("=" * 50)
    
    tests = [
        test_classifier,
        test_risk_agent,
        test_action_agent,
        test_audit_agent,
        test_dataset_manager,
        test_retrieval_agent,
        test_feedback_system
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems are working correctly!")
        print("✅ Your Content Moderation AI is ready!")
    else:
        print("⚠️  Some components need attention")
        print("❌ Check the failed tests above")

if __name__ == "__main__":
    main()
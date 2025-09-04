from flask import Flask, render_template, request, jsonify
from agents.classifier_agent import ClassifierAgent
from agents.risk_agent import RiskAgent
from agents.action_agent import ActionAgent
from agents.audit_agent import AuditAgent
from agents.retrieval_agent import RetrievalAgent  # COMMENTED OUT
from agents.communication_protocols import message_bus, Message
from utils.dataset_manager import DatasetManager
from utils.feedback_system import FeedbackSystem
import json

app = Flask(__name__)

# Initialize components
classifier = ClassifierAgent()
risk_assessor = RiskAgent()
action_decider = ActionAgent()
auditor = AuditAgent()
dataset_manager = DatasetManager()
retriever = RetrievalAgent(dataset_manager)  # COMMENTED OUT
feedback_system = FeedbackSystem()

# Setup message bus handlers
def classifier_handler(message):
    if message.message_type == "classify_text":
        classification = classifier.classify(message.data['text'])
        response = Message(
            "classifier_agent",
            message.sender,
            "classification_result",
            {'classification': classification, 'original_text': message.data['text']}
        )
        message_bus.send_message(response)

# Register agents with message bus
message_bus.register_agent("classifier_agent", classifier_handler)
message_bus.start_processing()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/moderate', methods=['POST'])
def moderate_content():
    try:
        data = request.json
        content = data['content']
        user_id = data.get('user_id', 'anonymous')
        
        # Classify content
        classification = classifier.classify(content)
        
        # Assess risk
        risk_assessment = risk_assessor.evaluate_risk(classification, content)
        
        # Decide actions
        actions = action_decider.determine_action(risk_assessment, classification, content)
        
        # Audit the decision
        explanation = auditor.generate_explanation(classification, risk_assessment)
        audit_entry = auditor.log_decision(
            content, user_id, classification, 
            risk_assessment, actions, explanation
        )
        
        # Add to dataset for future retrieval
        dataset_manager.add_to_dataset(
            content, user_id, classification, risk_assessment, actions
        )
        
        # Retrieve similar cases - TEMPORARILY DISABLED
        similar_cases = retriever.search_similar_content(classification)
        
        response = {
            'classification': classification,
            'risk_score': risk_assessment,
            'action': actions,
            'explanation': explanation,
            'similar_cases': similar_cases[:3]  # TEMPORARILY DISABLED
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit-stats')
def get_audit_stats():
    stats = auditor.get_audit_stats()
    return jsonify(stats)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        feedback_system.record_feedback(
            data['content'],
            data.get('user_id', 'anonymous'),
            data['accurate'],
            data.get('notes', ''),
           # data.get('expected_classification'),
           # data.get('expected_action')
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback-stats')
def get_feedback_stats():
    stats = feedback_system.get_feedback_stats()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
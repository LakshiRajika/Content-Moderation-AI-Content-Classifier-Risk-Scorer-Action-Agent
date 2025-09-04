import json
import threading
import time
from queue import Queue
from flask import Flask, request, jsonify
import requests

class Message:
    """Standardized message format for agent communication"""
    def __init__(self, sender, recipient, message_type, data, priority=1):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.data = data
        self.priority = priority  # 1=Low, 2=Medium, 3=High
        self.timestamp = time.time()
        self.message_id = f"{sender}_{recipient}_{self.timestamp}"
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'data': self.data,
            'priority': self.priority,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        message = cls(
            data['sender'],
            data['recipient'],
            data['message_type'],
            data['data'],
            data.get('priority', 1)
        )
        message.message_id = data['message_id']
        message.timestamp = data['timestamp']
        return message

class MessageBus:
    """Central message bus for agent communication (MCP - Message Control Protocol)"""
    def __init__(self):
        self.queues = {}  # Agent ID -> Queue
        self.subscriptions = {}  # Message type -> List of agent IDs
        self.handlers = {}  # Agent ID -> handler function
        self.running = False
    
    def register_agent(self, agent_id, handler=None):
        """Register an agent with the message bus"""
        self.queues[agent_id] = Queue()
        self.handlers[agent_id] = handler
    
    def subscribe(self, agent_id, message_type):
        """Subscribe an agent to a specific message type"""
        if message_type not in self.subscriptions:
            self.subscriptions[message_type] = []
        self.subscriptions[agent_id].append(message_type)
    
    def send_message(self, message):
        """Send a message to a specific agent"""
        if message.recipient in self.queues:
            self.queues[message.recipient].put(message)
            return True
        return False
    
    def broadcast(self, message_type, data, sender="system", priority=1):
        """Broadcast a message to all subscribers of a message type"""
        if message_type not in self.subscriptions:
            return False
        
        for agent_id in self.subscriptions[message_type]:
            message = Message(sender, agent_id, message_type, data, priority)
            self.queues[agent_id].put(message)
        
        return True
    
    def start_processing(self):
        """Start processing messages in the background"""
        self.running = True
        
        def process_messages():
            while self.running:
                for agent_id, queue in self.queues.items():
                    try:
                        message = queue.get_nowait()
                        if self.handlers[agent_id]:
                            self.handlers[agent_id](message)
                    except:
                        pass
                time.sleep(0.1)  # Prevent CPU spinning
        
        self.thread = threading.Thread(target=process_messages)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_processing(self):
        """Stop message processing"""
        self.running = False

class HTTPCommunicator:
    """HTTP-based communication for distributed agents"""
    def __init__(self, host='localhost', port=5000):
        self.base_url = f"http://{host}:{port}"
        self.endpoints = {}  # agent_id -> endpoint
    
    def register_endpoint(self, agent_id, endpoint):
        """Register an HTTP endpoint for an agent"""
        self.endpoints[agent_id] = endpoint
    
    def send_http_message(self, message):
        """Send a message via HTTP"""
        if message.recipient not in self.endpoints:
            return False
        
        endpoint = self.endpoints[message.recipient]
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                json=message.to_dict(),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Create global message bus instance
message_bus = MessageBus()
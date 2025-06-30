import os
import hmac
import hashlib
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

app = Flask(__name__)


MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI not found in environment variables")

client = MongoClient(MONGO_URI)
db = client.techstax_db 
events_collection = db.events 



@app.route('/')
def index():
    """Serves the frontend HTML page."""
    return render_template('index.html')

@app.route('/events')
def get_events():
    """API endpoint to fetch stored events from MongoDB."""
    
    events = list(events_collection.find().sort("timestamp", -1).limit(20))
    
    
    for event in events:
        event["_id"] = str(event["_id"])
        
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Endpoint that receives webhook events from GitHub."""
    
    
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.get_json()

    if not payload:
        return jsonify({"msg": "Invalid JSON payload"}), 400

    print(f"--- Received event: {event_type} ---")
    
    event_doc = None

    
    if event_type == 'push':
        pusher = payload.get('pusher', {}).get('name', 'Unknown')
        branch = payload.get('ref', 'refs/heads/unknown').split('/')[-1]
        commit_hash = payload.get('after', 'Unknown')
        
        event_doc = {
            "request_id": commit_hash,
            "author": pusher,
            "action": "PUSH",
            "from_branch": None, 
            "to_branch": branch,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    
    elif event_type == 'pull_request':
        action = payload.get('action')
        pr_data = payload.get('pull_request', {})
        
        
        if action == 'opened':
            author = pr_data.get('user', {}).get('login', 'Unknown')
            from_branch = pr_data.get('head', {}).get('ref', 'Unknown')
            to_branch = pr_data.get('base', {}).get('ref', 'Unknown')
            pr_id = str(pr_data.get('id', 'Unknown'))
            
            event_doc = {
                "request_id": pr_id,
                "author": author,
                "action": "PULL_REQUEST",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": pr_data.get('created_at', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }

        
        elif action == 'closed' and pr_data.get('merged') == True:
            author = pr_data.get('merged_by', {}).get('login', 'Unknown') 
            from_branch = pr_data.get('head', {}).get('ref', 'Unknown')
            to_branch = pr_data.get('base', {}).get('ref', 'Unknown')
            pr_id = str(pr_data.get('id', 'Unknown'))
            
            event_doc = {
                "request_id": pr_id,
                "author": author,
                "action": "MERGE",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": pr_data.get('merged_at', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
            }

    
    if event_doc:
        events_collection.insert_one(event_doc)
        print(f"Successfully stored event: {event_doc['action']}")
        return jsonify({"msg": f"Event {event_doc['action']} processed"}), 200
    else:
        return jsonify({"msg": "Event not relevant or handled"}), 200

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)
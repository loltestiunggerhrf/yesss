from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection (replace with your MongoDB URI)
client = MongoClient(os.getenv("MONGO_URI"))
db = client["key_system"]
keys_collection = db["keys"]

@app.route('/validate_key', methods=['GET'])
def validate_key():
    script_key = request.args.get('key')
    key_data = keys_collection.find_one({"key": script_key})
    
    if key_data:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure", "message": "Invalid key"})

# Dynamic port binding for Render
port = int(os.environ.get("PORT", 8080))  # Default to port 8080 if not set
app.run(host="0.0.0.0", port=port)  # Listen on all interfaces

if __name__ == "__main__":
    app.run()

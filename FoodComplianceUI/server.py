from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import sys

app = Flask(__name__, static_url_path='', static_folder='public')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    print("--- Received a request on /analyze ---", file=sys.stderr)
    data = request.get_json()
    print("Request data:", data, file=sys.stderr)
    
    text_block = data.get('text_block')
    
    if not text_block:
        return jsonify({"error": "Missing text_block"}), 400
        
    try:
        command = ["python3", "/home/student_01_ab8595ac0887/hackathon_project/main.py", text_block]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error executing main.py: {stderr.decode('utf-8')}", file=sys.stderr)
            return jsonify({"error": f"Error executing main.py: {stderr.decode('utf-8')}"}), 500
            
        results = json.loads(stdout.decode('utf-8'))
        print("Returning results:", results, file=sys.stderr)
        return jsonify(results)
        
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from backend.pipeline import get_chat_response, get_next_set

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    query = request.json['query']
    clear_history = request.json.get('clear_history', False)
    response, citations = get_chat_response(query, clear_history=clear_history)
    return jsonify({'response': response, 'citations': citations})

@app.route('/api/next', methods=['POST'])
def next_api():
    query = request.json['query']
    response, citations = get_next_set(query)
    return jsonify({'response': response, 'citations': citations})

if __name__ == '__main__':
    app.run(debug=True)
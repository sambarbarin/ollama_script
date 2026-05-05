from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
from ollama_client import OllamaClient
from database import ConversationDB

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Ollama client and database
ollama_client = OllamaClient()
db = ConversationDB()

# Store active streaming sessions
active_sessions = {}

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    """API endpoint to get available models"""
    if not ollama_client.is_available():
        return jsonify({
            'success': False,
            'error': 'Ollama API is not available. Make sure Ollama is running.'
        }), 503
    
    models = ollama_client.list_available_models()
    if models:
        return jsonify({
            'success': True,
            'models': models
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No models available'
        }), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if ollama_client.is_available() else 'unhealthy',
        'ollama_available': ollama_client.is_available()
    })

# New API endpoints for conversation management
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = db.get_conversations()
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        title = data.get('title', 'New Chat')
        model = data.get('model', 'llama3')
        
        conversation_id = db.create_conversation(title, model)
        conversation = db.get_conversation(conversation_id)
        
        return jsonify({
            'success': True,
            'conversation': conversation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation_detail(conversation_id):
    """Get conversation details and messages"""
    try:
        conversation = db.get_conversation(conversation_id)
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        messages = db.get_messages(conversation_id)
        conversation['messages'] = messages
        
        return jsonify({
            'success': True,
            'conversation': conversation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<int:conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    """Update conversation (e.g., rename title)"""
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        success = db.update_conversation_title(conversation_id, title)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        conversation = db.get_conversation(conversation_id)
        return jsonify({
            'success': True,
            'conversation': conversation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        success = db.delete_conversation(conversation_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Conversation deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/<int:conversation_id>/clear', methods=['POST'])
def clear_conversation_messages(conversation_id):
    """Clear all messages from a conversation"""
    try:
        conversation = db.get_conversation(conversation_id)
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        success = db.clear_conversation_messages(conversation_id)
        return jsonify({
            'success': True,
            'message': 'Conversation cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to chat server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Handle client joining a conversation"""
    conversation_id = data.get('conversation_id')
    
    if conversation_id:
        # Verify conversation exists
        conversation = db.get_conversation(conversation_id)
        if conversation:
            emit('conversation_joined', {
                'conversation_id': conversation_id,
                'conversation': conversation
            })
        else:
            emit('error', {'message': 'Conversation not found'})
    else:
        emit('status', {'message': 'No conversation specified'})

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat messages"""
    try:
        conversation_id = data.get('conversation_id')
        model = data.get('model', 'llama3')
        message = data.get('message', '')
        
        if not message.strip():
            emit('error', {'message': 'Empty message received'})
            return
        
        if not conversation_id:
            emit('error', {'message': 'No conversation ID provided'})
            return
        
        # Verify conversation exists
        conversation = db.get_conversation(conversation_id)
        if not conversation:
            emit('error', {'message': 'Conversation not found'})
            return
        
        # Add user message to database
        user_message_id = db.add_message(conversation_id, 'user', message)
        
        # Emit user message confirmation
        emit('message_received', {
            'role': 'user',
            'content': message,
            'conversation_id': conversation_id,
            'message_id': user_message_id
        })
        
        # Generate auto-title if this is the first user message
        messages = db.get_messages(conversation_id)
        user_messages = [m for m in messages if m['role'] == 'user']
        if len(user_messages) == 1:  # First user message
            auto_title = db.generate_auto_title(conversation_id)
            if auto_title and conversation['title'] == 'New Chat':
                db.update_conversation_title(conversation_id, auto_title)
                emit('conversation_title_updated', {
                    'conversation_id': conversation_id,
                    'title': auto_title
                })
        
        # Check if Ollama is available
        if not ollama_client.is_available():
            emit('error', {'message': 'Ollama API is not available. Please make sure Ollama is running.'})
            return
        
        # Start streaming response in a separate thread
        def stream_response():
            try:
                socketio.emit('response_start', {'conversation_id': conversation_id})
                
                # Get conversation messages for AI context
                conversation_messages = db.get_conversation_messages_for_api(conversation_id)
                
                assistant_response = ""
                for chunk in ollama_client.chat_stream(model, conversation_messages):
                    if chunk:
                        assistant_response += chunk
                        socketio.emit('response_chunk', {
                            'chunk': chunk,
                            'conversation_id': conversation_id
                        })
                
                # Add complete response to database
                if assistant_response:
                    assistant_message_id = db.add_message(conversation_id, 'assistant', assistant_response)
                    
                    socketio.emit('response_complete', {
                        'conversation_id': conversation_id,
                        'full_response': assistant_response,
                        'message_id': assistant_message_id
                    })
                
            except Exception as e:
                socketio.emit('error', {
                    'message': f'Error generating response: {str(e)}',
                    'conversation_id': conversation_id
                })
        
        # Start streaming in background thread
        thread = threading.Thread(target=stream_response)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        emit('error', {'message': f'Error processing message: {str(e)}'})

@socketio.on('load_conversation')
def handle_load_conversation(data):
    """Handle loading conversation messages"""
    try:
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            emit('error', {'message': 'No conversation ID provided'})
            return
        
        conversation = db.get_conversation(conversation_id)
        if not conversation:
            emit('error', {'message': 'Conversation not found'})
            return
        
        messages = db.get_messages(conversation_id)
        
        emit('conversation_loaded', {
            'conversation_id': conversation_id,
            'conversation': conversation,
            'messages': messages
        })
        
    except Exception as e:
        emit('error', {'message': f'Error loading conversation: {str(e)}'})

@socketio.on('clear_conversation')
def handle_clear_conversation(data):
    """Handle clearing conversation messages"""
    try:
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            emit('error', {'message': 'No conversation ID provided'})
            return
        
        success = db.clear_conversation_messages(conversation_id)
        if success:
            emit('conversation_cleared', {'conversation_id': conversation_id})
        else:
            emit('error', {'message': 'Failed to clear conversation'})
            
    except Exception as e:
        emit('error', {'message': f'Error clearing conversation: {str(e)}'})

if __name__ == '__main__':
    print("Starting Ollama Chat Web Interface...")
    print("Make sure Ollama is running on http://localhost:11434")
    print("Access the chat interface at: http://localhost:5000")
    
    # Run the app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
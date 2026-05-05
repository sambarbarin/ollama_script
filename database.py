import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ConversationDB:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
                )
            ''')
            
            # Create index for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                ON messages(conversation_id)
            ''')
            
            conn.commit()
    
    def create_conversation(self, title: str = "New Chat", model: str = "llama3") -> int:
        """Create a new conversation and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (title, model, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (title, model, datetime.now(), datetime.now()))
            
            conversation_id = cursor.lastrowid
            conn.commit()
            return conversation_id
    
    def get_conversations(self) -> List[Dict]:
        """Get all conversations ordered by updated_at desc"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.title, c.model, c.created_at, c.updated_at,
                       COUNT(m.id) as message_count,
                       MAX(m.timestamp) as last_message_time
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            ''')
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row[0],
                    'title': row[1],
                    'model': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'message_count': row[5],
                    'last_message_time': row[6]
                })
            
            return conversations
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Get a specific conversation by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, model, created_at, updated_at
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'model': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                }
            return None
    
    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update conversation title"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations 
                SET title = ?, updated_at = ?
                WHERE id = ?
            ''', (title, datetime.now(), conversation_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def update_conversation_timestamp(self, conversation_id: int):
        """Update conversation's updated_at timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), conversation_id))
            conn.commit()
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        """Add a message to a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add the message
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, role, content, datetime.now()))
            
            message_id = cursor.lastrowid
            
            # Update conversation timestamp
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), conversation_id))
            
            conn.commit()
            return message_id
    
    def get_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, role, content, timestamp
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'role': row[1],
                    'content': row[2],
                    'timestamp': row[3]
                })
            
            return messages
    
    def get_conversation_messages_for_api(self, conversation_id: int) -> List[Dict]:
        """Get messages formatted for Ollama API (role + content only)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1]
                })
            
            return messages
    
    def clear_conversation_messages(self, conversation_id: int) -> bool:
        """Clear all messages from a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def generate_auto_title(self, conversation_id: int) -> Optional[str]:
        """Generate intelligent auto title from first user message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT content
                FROM messages
                WHERE conversation_id = ? AND role = 'user'
                ORDER BY timestamp ASC
                LIMIT 1
            ''', (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                content = row[0].strip()
                
                # Generate a smart summary title
                title = self._create_smart_title(content)
                return title
            
            return None
    
    def _create_smart_title(self, message: str) -> str:
        """Create an intelligent title from the user's message"""
        # Clean up the message
        message = " ".join(message.split())
        
        # Common question patterns and their simplified forms
        question_patterns = [
            (r'^(comment|how do|how can|how to|comment faire|comment puis-je)', 'Comment'),
            (r'^(qu\'est-ce que|what is|what are|c\'est quoi)', 'Qu\'est-ce que'),
            (r'^(pourquoi|why|pour quelle raison)', 'Pourquoi'),
            (r'^(où|where|ou se trouve)', 'Où'),
            (r'^(quand|when|à quel moment)', 'Quand'),
            (r'^(qui|who|quelle personne)', 'Qui'),
            (r'^(quel|quelle|which|what)', 'Quel'),
            (r'^(peux-tu|can you|pouvez-vous|could you)', 'Aide pour'),
            (r'^(aide|help|aidez)', 'Aide avec'),
            (r'^(créer|create|faire|make|générer)', 'Créer'),
            (r'^(expliquer|explain|explique)', 'Explication'),
            (r'^(résoudre|solve|résous)', 'Résoudre'),
            (r'^(optimiser|optimize)', 'Optimisation'),
            (r'^(déboguer|debug|corriger)', 'Debug'),
            (r'^(installer|install)', 'Installation'),
            (r'^(configurer|configure|setup)', 'Configuration'),
        ]
        
        # Try to match question patterns
        import re
        for pattern, prefix in question_patterns:
            if re.search(pattern, message.lower()):
                # Extract the main subject after the question word
                remaining = re.sub(pattern, '', message, flags=re.IGNORECASE).strip()
                if remaining:
                    # Take first meaningful words and create title
                    words = remaining.split()[:6]  # Limit to 6 words
                    subject = ' '.join(words)
                    title = f"{prefix} {subject}"
                    if len(title) > 50:
                        title = title[:47] + "..."
                    return title
        
        # If no pattern matches, extract key terms and create a descriptive title
        title = self._extract_key_terms(message)
        return title
    
    def _extract_key_terms(self, message: str) -> str:
        """Extract key terms from message to create a descriptive title"""
        # Remove common stop words
        stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'da', 'dans', 'avec', 'pour',
            'sur', 'par', 'en', 'et', 'ou', 'si', 'mais', 'donc', 'car', 'comme', 'que',
            'qui', 'dont', 'où', 'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'votre', 'leur',
            'ce', 'cette', 'ces', 'cet', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on',
            'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        # Split into words and filter
        words = message.lower().split()
        meaningful_words = [
            word.strip('.,!?;:()[]{}"\'-') 
            for word in words 
            if len(word.strip('.,!?;:()[]{}"\'-')) > 2 
            and word.lower().strip('.,!?;:()[]{}"\'-') not in stop_words
        ]
        
        # Take first 4-5 meaningful words
        key_words = meaningful_words[:5]
        
        if len(key_words) == 0:
            # Fallback: use first 40 characters
            title = message[:40]
            if len(message) > 40:
                title += "..."
        else:
            # Capitalize first word and create title
            title = ' '.join(key_words)
            title = title[0].upper() + title[1:] if title else "Conversation"
            
        # Ensure reasonable length
        if len(title) > 50:
            title = title[:47] + "..."
            
        return title
    
    def close(self):
        """Close database connection (not needed with context managers, but good practice)"""
        pass
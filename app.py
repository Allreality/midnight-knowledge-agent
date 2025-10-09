# File: app.py
# Path: ~/knowledgeagent/app.py

from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
import os
import json
import sqlite3
from datetime import datetime
import markdown
import re

app = Flask(__name__)

@app.route('/midnight')
def midnight():
    return render_template('midnight.html')

# Configuration
KNOWLEDGE_BASE_DIR = Path('knowledge_base')
DATABASE_PATH = Path('research_tasks.db')

# Ensure directories exist
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            context TEXT,
            source_type TEXT DEFAULT 'manual',
            source_url TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def scan_documents():
    """Scan knowledge base directory for documents"""
    documents = []
    
    if not KNOWLEDGE_BASE_DIR.exists():
        return documents
    
    for file_path in KNOWLEDGE_BASE_DIR.rglob('*.md'):
        stat = file_path.stat()
        rel_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        
        documents.append({
            'name': file_path.name,
            'relative_path': str(rel_path),
            'size': stat.st_size,
            'modified': stat.st_mtime
        })
    
    # Sort by modified time, newest first
    documents.sort(key=lambda x: x['modified'], reverse=True)
    
    return documents

def categorize_documents(documents):
    """Categorize documents based on their path or filename"""
    categories = {
        'midnight': {'count': 0, 'size': 0},
        'cardano': {'count': 0, 'size': 0},
        'healthcare': {'count': 0, 'size': 0},
        'zkproofs': {'count': 0, 'size': 0},
        'smart_contracts': {'count': 0, 'size': 0},
        'architecture': {'count': 0, 'size': 0},
        'competitors': {'count': 0, 'size': 0},
        'research': {'count': 0, 'size': 0}
    }
    
    for doc in documents:
        path = doc['relative_path'].lower()
        name = doc['name'].lower()
        size = doc['size']
        
        categorized = False
        
        # Check filename FIRST for specific keywords (higher priority)
        if 'smart_contract' in name or 'smartcontract' in name or 'plutus' in name:
            categories['smart_contracts']['count'] += 1
            categories['smart_contracts']['size'] += size
            categorized = True
        elif 'zkproof' in name or 'zk_proof' in name or 'zero_knowledge' in name or 'zero-knowledge' in name:
            categories['zkproofs']['count'] += 1
            categories['zkproofs']['size'] += size
            categorized = True
        elif 'healthcare' in name or 'health' in name:
            categories['healthcare']['count'] += 1
            categories['healthcare']['size'] += size
            categorized = True
        elif 'architecture' in name:
            categories['architecture']['count'] += 1
            categories['architecture']['size'] += size
            categorized = True
        elif 'competitor' in name:
            categories['competitors']['count'] += 1
            categories['competitors']['size'] += size
            categorized = True
        
        # If not categorized by filename, check path
        if not categorized:
            if path.startswith('midnight'):
                categories['midnight']['count'] += 1
                categories['midnight']['size'] += size
            elif path.startswith('cardano'):
                categories['cardano']['count'] += 1
                categories['cardano']['size'] += size
            elif path.startswith('healthcare'):
                categories['healthcare']['count'] += 1
                categories['healthcare']['size'] += size
            elif path.startswith('zkproofs') or path.startswith('zk'):
                categories['zkproofs']['count'] += 1
                categories['zkproofs']['size'] += size
            elif path.startswith('smart_contracts') or path.startswith('smartcontracts'):
                categories['smart_contracts']['count'] += 1
                categories['smart_contracts']['size'] += size
            elif path.startswith('architecture'):
                categories['architecture']['count'] += 1
                categories['architecture']['size'] += size
            elif path.startswith('competitors'):
                categories['competitors']['count'] += 1
                categories['competitors']['size'] += size
            elif path.startswith('research'):
                categories['research']['count'] += 1
                categories['research']['size'] += size
            elif 'midnight' in name:
                categories['midnight']['count'] += 1
                categories['midnight']['size'] += size
            elif 'cardano' in name:
                categories['cardano']['count'] += 1
                categories['cardano']['size'] += size
            # In app.py - already works!
            elif path.startswith('cardano'):
                categories['cardano']['count'] += 1
                categories['cardano']['size'] += size
            elif 'cardano' in name:  # This catches "Cardano_Node" files
                categories['cardano']['count'] += 1
                categories['cardano']['size'] += size
            else:
                # Default to research if no specific category matches
                categories['research']['count'] += 1
                categories['research']['size'] += size
    
    return categories

# Routes

@app.route('/')
def index():
    """Render the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    documents = scan_documents()
    categories = categorize_documents(documents)
    
    total_size = sum(doc['size'] for doc in documents)
    total_size_kb = round(total_size / 1024, 1)
    
    return jsonify({
        'total_documents': len(documents),
        'total_size_kb': total_size_kb,
        'categories': categories
    })

@app.route('/api/recent')
def get_recent():
    """Get recent documents"""
    limit = request.args.get('limit', 50, type=int)
    category = request.args.get('category', '')
    
    documents = scan_documents()
    
    # Filter by category if specified
    if category:
        filtered = []
        for doc in documents:
            path = doc['relative_path'].lower()
            name = doc['name'].lower()
            
            # Match category - filename takes priority
            matches = False
            if category == 'smart_contracts':
                matches = 'plutus' in name or 'smart_contract' in name or path.startswith('smart_contracts')
            elif category == 'zkproofs':
                matches = 'zkproof' in name or 'zk' in name or path.startswith('zkproofs')
            else:
                matches = path.startswith(category.lower()) or category.lower() in name
            
            if matches:
                filtered.append(doc)
        
        documents = filtered
    
    # Limit results
    documents = documents[:limit]
    
    return jsonify({
        'documents': documents,
        'total': len(documents)
    })

@app.route('/api/document/<path:doc_path>')
def get_document(doc_path):
    """Get document content"""
    file_path = KNOWLEDGE_BASE_DIR / doc_path
    
    if not file_path.exists():
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        content = file_path.read_text(encoding='utf-8')
        html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        return jsonify({
            'content': content,
            'html': html
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/document/<path:doc_path>', methods=['DELETE'])
def delete_document(doc_path):
    """Delete a document"""
    file_path = KNOWLEDGE_BASE_DIR / doc_path
    
    if not file_path.exists():
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        file_path.unlink()
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple documents"""
    data = request.get_json()
    paths = data.get('paths', [])
    
    deleted = []
    errors = []
    
    for path in paths:
        file_path = KNOWLEDGE_BASE_DIR / path
        try:
            if file_path.exists():
                file_path.unlink()
                deleted.append(path)
            else:
                errors.append(f"{path}: Not found")
        except Exception as e:
            errors.append(f"{path}: {str(e)}")
    
    return jsonify({
        'message': f'Deleted {len(deleted)} document(s)',
        'deleted': deleted,
        'errors': errors
    })

@app.route('/api/tasks')
def get_tasks():
    """Get all research tasks"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row['id'],
            'topic': row['topic'],
            'context': row['context'],
            'source_type': row['source_type'],
            'source_url': row['source_url'],
            'status': row['status'],
            'created_at': row['created_at'],
            'completed_at': row['completed_at'],
            'error': row['error']
        })
    
    conn.close()
    
    return jsonify({'tasks': tasks})

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new research task"""
    data = request.get_json()
    
    topic = data.get('topic')
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    context = data.get('context', '')
    source_type = data.get('source_type', 'manual')
    source_url = data.get('source_url', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (topic, context, source_type, source_url, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (topic, context, source_type, source_url))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Task created successfully',
        'task_id': task_id
    }), 201

@app.route('/api/tasks/<int:task_id>/approve', methods=['POST'])
def approve_task(task_id):
    """Approve a task and queue it for processing"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', ('approved', task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task approved'})

@app.route('/api/tasks/<int:task_id>/deny', methods=['POST'])
def deny_task(task_id):
    """Deny a task"""
    data = request.get_json()
    reason = data.get('reason', 'Denied by user')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE tasks SET status = ?, error = ? WHERE id = ?', 
                   ('denied', reason, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task denied'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task deleted'})

@app.route('/api/search')
def search():
    """Search documents"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'results': [], 'total': 0})
    
    results = []
    documents = scan_documents()
    
    for doc in documents:
        file_path = KNOWLEDGE_BASE_DIR / doc['relative_path']
        try:
            content = file_path.read_text(encoding='utf-8')
            if query in content.lower():
                # Find context around the match
                lines = content.split('\n')
                matched_lines = [line for line in lines if query in line.lower()]
                preview = '\n'.join(matched_lines[:3])
                
                results.append({
                    'relative_path': doc['relative_path'],
                    'name': doc['name'],
                    'preview': preview[:500]
                })
        except Exception as e:
            print(f"Error searching {doc['relative_path']}: {e}")
    
    return jsonify({
        'results': results,
        'total': len(results)
    })

if __name__ == '__main__':
    init_db()
    print(f"Knowledge base directory: {KNOWLEDGE_BASE_DIR.absolute()}")
    print(f"Database: {DATABASE_PATH.absolute()}")
    app.run(debug=True, port=5000)
#!/usr/bin/env python3
"""
Knowledge Base Web Dashboard
Interactive web interface for managing your knowledge base
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import os
import json
from datetime import datetime
import markdown2
from kb_agent_system_claude import KnowledgeBase, AgentOrchestrator
import threading
import queue
from typing import List, Dict  # ADD THIS LINE IF MISSING

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Global queue for research tasks
research_queue = queue.Queue()
research_results = {}

# Initialize KB
kb = KnowledgeBase()
orchestrator = AgentOrchestrator(kb)

class ResearchTask:
    def __init__(self, task_id, topic, context, source_type, source_url, status="pending"):
        self.task_id = task_id
        self.topic = topic
        self.context = context
        self.source_type = source_type  # 'webpage', 'youtube', 'medium', 'manual'
        self.source_url = source_url
        self.status = status  # 'pending', 'approved', 'denied', 'processing', 'completed', 'error'
        self.created_at = datetime.now()
        self.result = None
        self.error = None

# In-memory task storage (use database in production)
tasks = {}
task_counter = 0

def background_researcher():
    """Background thread to process approved research tasks"""
    while True:
        try:
            task_id = research_queue.get(timeout=1)
            if task_id not in tasks:
                continue
            
            task = tasks[task_id]
            task.status = "processing"
            
            try:
                # Build context with source info
                full_context = task.context
                if task.source_url:
                    full_context += f"\n\nSource URL: {task.source_url}"
                    full_context += f"\nSource Type: {task.source_type}"
                
                # Perform research
                result = orchestrator.research_and_document(
                    topic=task.topic,
                    context=full_context,
                    doc_type="guide",
                    target_audience="developers"
                )
                
                task.result = result
                task.status = "completed"
                research_results[task_id] = result
                
            except Exception as e:
                task.error = str(e)
                task.status = "error"
                print(f"[Background] Error processing task {task_id}: {e}")
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"[Background] Researcher error: {e}")

# Start background thread
researcher_thread = threading.Thread(target=background_researcher, daemon=True)
researcher_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """Get knowledge base statistics"""
    categories = {}
    total = 0
    total_size = 0
    
    for category in kb.categories.keys():
        cat_path = os.path.join(kb.base_path, category)
        if os.path.exists(cat_path):
            files = [f for f in os.listdir(cat_path) if f.endswith('.md')]
            count = len(files)
            categories[category] = {
                'count': count,
                'description': kb.categories[category]
            }
            total += count
            
            for f in files:
                total_size += os.path.getsize(os.path.join(cat_path, f))
    
    return jsonify({
        'total_documents': total,
        'total_size_kb': round(total_size / 1024, 1),
        'categories': categories,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/recent')
def api_recent():
    """Get recent documents"""
    category = request.args.get('category')
    limit = int(request.args.get('limit', 10))
    
    search_path = os.path.join(kb.base_path, category) if category else kb.base_path
    
    files = []
    for root, dirs, filenames in os.walk(search_path):
        for f in filenames:
            if f.endswith('.md') and f != 'INDEX.md':
                filepath = Path(root) / f
                files.append({
                    'path': str(filepath),
                    'relative_path': str(filepath.relative_to(kb.base_path)),
                    'name': f,
                    'modified': filepath.stat().st_mtime,
                    'size': filepath.stat().st_size
                })
    
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify({
        'documents': files[:limit],
        'total': len(files)
    })

@app.route('/api/document/<path:doc_path>', methods=['DELETE'])
def api_delete_document(doc_path):
    """Delete a document"""
    filepath = os.path.join(kb.base_path, doc_path)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        # Delete the file
        os.remove(filepath)
        
        # Regenerate index
        orchestrator.maintainer_agent.create_index()
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/bulk-delete', methods=['POST'])
def api_bulk_delete():
    """Delete multiple documents"""
    data = request.json
    paths = data.get('paths', [])
    
    deleted = []
    errors = []
    
    for doc_path in paths:
        filepath = os.path.join(kb.base_path, doc_path)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted.append(doc_path)
            else:
                errors.append(f"{doc_path}: Not found")
        except Exception as e:
            errors.append(f"{doc_path}: {str(e)}")
    
    # Regenerate index
    if deleted:
        orchestrator.maintainer_agent.create_index()
    
    return jsonify({
        'success': len(deleted) > 0,
        'deleted': deleted,
        'errors': errors,
        'message': f'Deleted {len(deleted)} documents'
    })

@app.route('/api/documents/cleanup', methods=['POST'])
def api_cleanup_errors():
    """Clean up all error documents"""
    data = request.json
    confirm = data.get('confirm', False)
    
    if not confirm:
        return jsonify({'error': 'Confirmation required'}), 400
    
    error_files = []
    
    # Find all error documents
    for root, dirs, files in os.walk(kb.base_path):
        for file in files:
            if 'error' in file.lower() or 'Error' in file:
                filepath = os.path.join(root, file)
                error_files.append(filepath)
    
    # Delete them
    deleted = []
    for filepath in error_files:
        try:
            os.remove(filepath)
            deleted.append(filepath)
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")
    
    # Regenerate index
    if deleted:
        orchestrator.maintainer_agent.create_index()
    
    return jsonify({
        'success': True,
        'deleted': len(deleted),
        'files': deleted,
        'message': f'Cleaned up {len(deleted)} error documents'
    })

@app.route('/api/search')
def api_search():
    """Search documents"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': [], 'query': query})
    
    results = kb.search(query)
    
    docs = []
    for filepath in results[:20]:  # Limit to 20 results
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Extract first few lines as preview
                lines = content.split('\n')
                preview = '\n'.join(lines[:5])
            
            docs.append({
                'path': filepath,
                'relative_path': str(Path(filepath).relative_to(kb.base_path)),
                'preview': preview
            })
        except:
            pass
    
    return jsonify({
        'results': docs,
        'query': query,
        'total': len(results)
    })

@app.route('/api/document/<path:doc_path>')
def api_document(doc_path):
    """Get document content"""
    filepath = os.path.join(kb.base_path, doc_path)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables', 'metadata'])
        
        return jsonify({
            'path': doc_path,
            'content': content,
            'html': html,
            'metadata': html.metadata if hasattr(html, 'metadata') else {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def synthesize_documentation(self, research_files: List[str], 
                              doc_type: str = "guide",
                              target_audience: str = "developers") -> Dict:
    """Take raw research and create polished documentation using Claude"""
    print(f"[{self.name}] Synthesizing documentation from {len(research_files)} sources")
    
    try:
        # Read all research files
        research_content = []
        topic = ""  # Extract topic from research
        context = ""
        source_url = ""
        
        for file_path in research_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    research_content.append(f"## Source: {file_path}\n\n{content}\n\n")
                    
                    # Try to extract metadata from first file
                    if not topic:
                        import json
                        lines = content.split('\n')
                        if lines[0] == '---' and '---' in lines[1:]:
                            end_idx = lines[1:].index('---') + 1
                            try:
                                metadata = json.loads('\n'.join(lines[1:end_idx]))
                                topic = metadata.get('title', '')
                            except:
                                pass
                        
                        # Extract topic from filename if not in metadata
                        if not topic:
                            import os
                            filename = os.path.basename(file_path)
                            topic = filename.replace('.md', '').replace('_', ' ')
                            # Remove timestamp prefix
                            parts = topic.split(' ', 1)
                            if len(parts) > 1 and parts[0].replace('_', '').isdigit():
                                topic = parts[1]
                    
            except Exception as e:
                print(f"[{self.name}] Warning: Could not read {file_path}: {e}")
        
        if not research_content:
            raise ValueError("No research content available to synthesize")
        
        combined_research = "\n".join(research_content)
        
        # **NEW: Detect category smartly**
        category = self._detect_category(topic, combined_research[:500], source_url)
        
        # Create prompt for Claude
        prompt = f"""You are a technical documentation writer. Please synthesize the following research into a clear, well-structured {doc_type} for {target_audience}.

Research Material:
{combined_research}

Please create comprehensive documentation that:
1. Has a clear title and introduction
2. Is well-organized with proper headings
3. Includes code examples where relevant
4. Explains concepts clearly for {target_audience}
5. Includes practical implementation guidance
6. Has a summary or conclusion

Format the output in clean Markdown."""

        # Call Claude API with retry logic
        response = self._call_claude_with_retry(prompt)
        
        # Extract the documentation
        documentation = response.content[0].text
        
        # Extract title from first heading or use default
        lines = documentation.split('\n')
        title = "Documentation"
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        return {
            "title": title,
            "type": doc_type,
            "content": documentation,
            "category": category,  # Use detected category
            "written_by": MODEL_NAME,
            "sources": research_files,
            "model": response.model
        }
        
    except Exception as e:
        print(f"[{self.name}] Error creating documentation: {e}")
        return self._create_error_fallback(research_files, str(e))

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """Get all research tasks"""
    task_list = []
    for task_id, task in tasks.items():
        task_list.append({
            'id': task.task_id,
            'topic': task.topic,
            'context': task.context,
            'source_type': task.source_type,
            'source_url': task.source_url,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'result': task.result,
            'error': task.error
        })
    
    task_list.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'tasks': task_list})

@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """Create a new research task"""
    global task_counter
    
    data = request.json
    
    task_counter += 1
    task = ResearchTask(
        task_id=task_counter,
        topic=data.get('topic', ''),
        context=data.get('context', ''),
        source_type=data.get('source_type', 'manual'),
        source_url=data.get('source_url', '')
    )
    
    tasks[task_counter] = task
    
    return jsonify({
        'success': True,
        'task_id': task_counter,
        'message': 'Task created. Awaiting approval.'
    })

@app.route('/api/tasks/<int:task_id>/approve', methods=['POST'])
def api_approve_task(task_id):
    """Approve a research task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_id]
    task.status = "approved"
    
    # Add to research queue
    research_queue.put(task_id)
    
    return jsonify({
        'success': True,
        'message': 'Task approved and queued for research'
    })

@app.route('/api/tasks/<int:task_id>/deny', methods=['POST'])
def api_deny_task(task_id):
    """Deny a research task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_id]
    task.status = "denied"
    
    reason = request.json.get('reason', 'No reason provided')
    task.error = f"Denied: {reason}"
    
    return jsonify({
        'success': True,
        'message': 'Task denied'
    })

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete a research task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    del tasks[task_id]
    
    return jsonify({
        'success': True,
        'message': 'Task deleted'
    })

@app.route('/api/analyze-gaps', methods=['POST'])
def api_analyze_gaps():
    """Run knowledge gap analysis"""
    try:
        gaps = orchestrator.analyze_and_plan()
        
        return jsonify({
            'success': True,
            'analysis': gaps
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Knowledge Base Web Dashboard")
    print("="*60)
    print("\n📊 Starting server...")
    print("🔗 Open your browser to: http://localhost:5000")
    print("\n⚠️  Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

class DocumentationWriterAgent:
    """Agent responsible for creating clean documentation with Claude"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "Documentation Writer"
    
    def _detect_category(self, topic: str, context: str, source_url: str) -> str:
        """
        Smart category detection based on content analysis
        """
        # Combine all text for analysis
        combined_text = f"{topic} {context} {source_url}".lower()
        
        # Category keywords with weights
        category_patterns = {
            'cardano': {
                'keywords': ['cardano', 'ada', 'plutus', 'stake pool', 'catalyst', 
                            'daedalus', 'yoroi', 'shelley', 'voltaire', 'goguen',
                            'docs.cardano.org', 'cardano.org'],
                'weight': 0
            },
            'midnight': {
                'keywords': ['midnight', 'midnight network', 'dust', 'compact',
                            'midnight.network', 'privacy blockchain'],
                'weight': 0
            },
            'healthcare': {
                'keywords': ['healthcare', 'health', 'medical', 'patient', 'hipaa',
                            'fhir', 'hl7', 'ehr', 'emr', 'clinical', 'hospital',
                            'doctor', 'pharma', 'drug', 'diagnosis'],
                'weight': 0
            },
            'zkproofs': {
                'keywords': ['zero knowledge', 'zk-proof', 'zkp', 'zk-snark', 
                            'zk-stark', 'zero-knowledge', 'proof system',
                            'cryptographic proof', 'privacy proof'],
                'weight': 0
            },
            'smart_contracts': {
                'keywords': ['smart contract', 'solidity', 'vyper', 'contract',
                            'dapp', 'decentralized app', 'on-chain'],
                'weight': 0
            },
            'architecture': {
                'keywords': ['architecture', 'design pattern', 'system design',
                            'infrastructure', 'scalability', 'distributed system',
                            'consensus', 'protocol'],
                'weight': 0
            },
            'competitors': {
                'keywords': ['ethereum', 'polkadot', 'cosmos', 'avalanche',
                            'solana', 'algorand', 'near', 'comparison', 'vs'],
                'weight': 0
            }
        }
        
        # Calculate weights for each category
        for category, data in category_patterns.items():
            for keyword in data['keywords']:
                if keyword in combined_text:
                    # Weight increases based on keyword match
                    data['weight'] += combined_text.count(keyword)
        
        # Find category with highest weight
        max_weight = 0
        best_category = 'research'  # Default fallback
        
        for category, data in category_patterns.items():
            if data['weight'] > max_weight:
                max_weight = data['weight']
                best_category = category
        
        # If no strong match, use 'midnight' as default for blockchain topics
        if max_weight == 0:
            if any(word in combined_text for word in ['blockchain', 'crypto', 'token', 'wallet']):
                best_category = 'midnight'
        
        print(f"[{self.name}] Category detection: '{best_category}' (confidence: {max_weight})")
        return best_category
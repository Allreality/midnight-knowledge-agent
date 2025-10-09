#!/usr/bin/env python3
"""
Research Worker - Monitors database and processes approved tasks
"""

import sqlite3
import time
import sys
import shutil
from pathlib import Path
from datetime import datetime
from kb_agent_system_claude import AgentOrchestrator, KnowledgeBase

DATABASE_PATH = Path('research_tasks.db')
CHECK_INTERVAL = 5  # seconds
KB_DIR = Path('knowledge_base')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def determine_category(topic, context=''):
    """Determine the best category for a topic"""
    topic_lower = topic.lower()
    context_lower = context.lower()
    combined = topic_lower + ' ' + context_lower
    
    # Check for specific keywords
    if any(word in combined for word in ['plutus', 'aiken', 'marlowe', 'smart contract', 'smartcontract', 'contract']):
        return 'smart_contracts'
    elif any(word in combined for word in ['midnight', 'zk', 'zero-knowledge', 'zero knowledge', 'zkproof']):
        return 'midnight'
    elif any(word in combined for word in ['cardano', 'ada', 'stake pool', 'node']):
        return 'cardano'
    elif any(word in combined for word in ['healthcare', 'health', 'medical']):
        return 'healthcare'
    elif any(word in combined for word in ['competitor', 'ethereum', 'solana', 'polkadot']):
        return 'competitors'
    elif any(word in combined for word in ['architecture', 'design', 'system']):
        return 'architecture'
    else:
        return 'research'

def move_files_to_category(research_file, doc_file, category):
    """Move generated files to the correct category folder"""
    category_dir = KB_DIR / category
    category_dir.mkdir(exist_ok=True)
    
    moved_files = {}
    
    # Move research file
    if research_file and Path(research_file).exists():
        src = Path(research_file)
        dst = category_dir / src.name
        shutil.move(str(src), str(dst))
        moved_files['research'] = str(dst)
        print(f"   📁 Moved research to: {category}/{src.name}")
    
    # Move documentation file
    if doc_file and Path(doc_file).exists():
        src = Path(doc_file)
        dst = category_dir / src.name
        shutil.move(str(src), str(dst))
        moved_files['documentation'] = str(dst)
        print(f"   📁 Moved documentation to: {category}/{src.name}")
    
    return moved_files

def process_task(task):
    """Process a single research task"""
    print(f"\n{'='*60}")
    print(f"Processing task #{task['id']}: {task['topic']}")
    print(f"{'='*60}\n")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Determine category
        category = determine_category(task['topic'], task['context'] or '')
        print(f"📂 Category: {category}")
        
        # Update status to processing
        cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', 
                      ('processing', task['id']))
        conn.commit()
        
        # Initialize orchestrator
        kb = KnowledgeBase()
        orchestrator = AgentOrchestrator(kb)
        
        # Perform research
        result = orchestrator.research_and_document(
            topic=task['topic'],
            context=task['context'] or '',
            doc_type='guide',
            target_audience='developers'
        )
        
        # Move files to correct category
        moved = move_files_to_category(
            result.get('research_file'),
            result.get('documentation_file'),
            category
        )
        
        # Mark as completed
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, completed_at = ? 
            WHERE id = ?
        ''', ('completed', datetime.now().isoformat(), task['id']))
        conn.commit()
        
        print(f"\n✅ Task #{task['id']} completed successfully!")
        print(f"   Category: {category}")
        if moved.get('research'):
            print(f"   Research: {moved['research']}")
        if moved.get('documentation'):
            print(f"   Documentation: {moved['documentation']}")
        
    except Exception as e:
        # Mark as error
        error_msg = str(e)
        print(f"\n❌ Error processing task #{task['id']}: {error_msg}")
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, error = ? 
            WHERE id = ?
        ''', ('error', error_msg, task['id']))
        conn.commit()
    
    finally:
        conn.close()

def main():
    """Main worker loop"""
    print("="*60)
    print("Research Worker Started (with Auto-Categorization)")
    print("="*60)
    print(f"Database: {DATABASE_PATH.absolute()}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    if not DATABASE_PATH.exists():
        print(f"❌ Database not found: {DATABASE_PATH}")
        sys.exit(1)
    
    try:
        while True:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get next approved task
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE status = 'approved' 
                ORDER BY created_at ASC 
                LIMIT 1
            ''')
            
            task = cursor.fetchone()
            conn.close()
            
            if task:
                process_task(task)
            else:
                # No tasks, wait
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No approved tasks. Waiting...", end='\r')
                time.sleep(CHECK_INTERVAL)
                
    except KeyboardInterrupt:
        print("\n\n👋 Worker stopped by user")
    except Exception as e:
        print(f"\n❌ Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

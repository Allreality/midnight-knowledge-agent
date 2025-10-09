#!/usr/bin/env python3
"""
Knowledge Base CLI Tool
Manage your Midnight blockchain knowledge base
"""
import sys
import os
from pathlib import Path
from kb_agent_system_claude import KnowledgeBase, AgentOrchestrator

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def show_help():
    """Display help information"""
    print("""
Knowledge Base CLI Tool - Midnight Blockchain Research
=====================================================

Usage:
  ./kb_cli.py <command> [arguments]

Commands:
  research <topic> [context]    Research a topic and create documentation
  search <query>                Search the knowledge base
  gaps                          Analyze knowledge gaps
  index                         Update the knowledge base index
  recent [category] [n]         Show recent documents (default: 10)
  stats                         Show knowledge base statistics
  view <filepath>               View a specific document
  categories                    List all categories
  outdated [days]               Find outdated documents (default: 30 days)

Examples:
  ./kb_cli.py research "Midnight Smart Contracts"
  ./kb_cli.py research "ZK Proofs" "Focus on healthcare applications"
  ./kb_cli.py search "privacy"
  ./kb_cli.py recent midnight 5
  ./kb_cli.py outdated 7
  ./kb_cli.py view ./knowledge_base/midnight/latest.md

Tips:
  - Use quotes for multi-word arguments
  - Add context to get more focused research
  - Run 'gaps' regularly to identify missing topics
    """)

def cmd_research(args):
    """Research a topic"""
    if len(args) < 1:
        print("❌ Error: Please provide a topic to research")
        print("Usage: ./kb_cli.py research '<topic>' ['<context>']")
        return
    
    topic = args[0]
    context = args[1] if len(args) > 1 else ""
    
    print_header(f"Researching: {topic}")
    
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    result = orchestrator.research_and_document(
        topic=topic,
        context=context,
        doc_type="guide",
        target_audience="developers"
    )
    
    print(f"\n✅ Research Complete!")
    print(f"📄 Documentation: {result['documentation_file']}")
    print(f"🔬 Research: {result['research_file']}")
    print(f"📚 Index: {result['index_file']}")

def cmd_search(args):
    """Search the knowledge base"""
    if len(args) < 1:
        print("❌ Error: Please provide a search query")
        print("Usage: ./kb_cli.py search '<query>'")
        return
    
    query = " ".join(args)
    print_header(f"Searching for: {query}")
    
    kb = KnowledgeBase()
    results = kb.search(query)
    
    if not results:
        print("❌ No documents found")
        return
    
    print(f"✅ Found {len(results)} documents:\n")
    for i, filepath in enumerate(results, 1):
        rel_path = Path(filepath).relative_to(kb.base_path)
        print(f"{i:2d}. {rel_path}")
    
    # Show preview of first result
    if results:
        print(f"\n📄 Preview of first result:")
        print("-" * 60)
        with open(results[0], 'r') as f:
            lines = f.readlines()
            for line in lines[:15]:  # First 15 lines
                print(line.rstrip())
        print("-" * 60)

def cmd_gaps(args):
    """Analyze knowledge gaps"""
    print_header("Analyzing Knowledge Gaps")
    
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    gaps = orchestrator.analyze_and_plan()
    print(gaps)

def cmd_index(args):
    """Update the knowledge base index"""
    print_header("Updating Knowledge Base Index")
    
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    index_file = orchestrator.maintainer_agent.create_index()
    print(f"✅ Index updated: {index_file}")

def cmd_recent(args):
    """Show recent documents"""
    category = args[0] if len(args) > 0 and args[0] in ["midnight", "research", "cardano", "healthcare", "zkproofs", "architecture"] else None
    limit = int(args[1]) if len(args) > 1 else 10
    
    print_header(f"Recent Documents{' in ' + category if category else ''}")
    
    kb = KnowledgeBase()
    search_path = os.path.join(kb.base_path, category) if category else kb.base_path
    
    files = []
    for root, dirs, filenames in os.walk(search_path):
        for f in filenames:
            if f.endswith('.md') and f != 'INDEX.md':
                filepath = Path(root) / f
                files.append((filepath.stat().st_mtime, filepath))
    
    files.sort(reverse=True)
    
    if not files:
        print("❌ No documents found")
        return
    
    print(f"Showing {min(limit, len(files))} of {len(files)} documents:\n")
    for i, (mtime, filepath) in enumerate(files[:limit], 1):
        rel_path = filepath.relative_to(kb.base_path)
        from datetime import datetime
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        print(f"{i:2d}. [{date_str}] {rel_path}")

def cmd_stats(args):
    """Show knowledge base statistics"""
    print_header("Knowledge Base Statistics")
    
    kb = KnowledgeBase()
    categories = {}
    total = 0
    total_size = 0
    
    for category in kb.categories.keys():
        cat_path = os.path.join(kb.base_path, category)
        if os.path.exists(cat_path):
            files = [f for f in os.listdir(cat_path) if f.endswith('.md')]
            count = len(files)
            categories[category] = count
            total += count
            
            # Calculate size
            for f in files:
                total_size += os.path.getsize(os.path.join(cat_path, f))
    
    print(f"📊 Total Documents: {total}")
    print(f"💾 Total Size: {total_size / 1024:.1f} KB\n")
    print("Category Breakdown:")
    print("-" * 60)
    
    max_count = max(categories.values()) if categories else 1
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {cat:20s} {count:3d} ({percentage:5.1f}%) {bar}")

def cmd_view(args):
    """View a specific document"""
    if len(args) < 1:
        print("❌ Error: Please provide a file path")
        print("Usage: ./kb_cli.py view <filepath>")
        return
    
    filepath = args[0]
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        return
    
    print_header(f"Viewing: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
        print(content)

def cmd_cleanup(args):
    """Clean up error documents with selection"""
    print_header("Error Document Cleanup")
    
    kb = KnowledgeBase()
    error_files = []
    
    # Find all error documents
    for root, dirs, files in os.walk(kb.base_path):
        for file in files:
            if ('error' in file.lower() or 'Error' in file) and file.endswith('.md'):
                filepath = os.path.join(root, file)
                error_files.append(filepath)
    
    if not error_files:
        print("✅ No error documents found")
        return
    
    print(f"Found {len(error_files)} error document(s):\n")
    
    # Show list with numbers
    for i, filepath in enumerate(error_files, 1):
        rel_path = Path(filepath).relative_to(kb.base_path)
        stat = os.stat(filepath)
        size = stat.st_size / 1024  # KB
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"{i:2d}. {rel_path}")
        print(f"    Size: {size:.1f} KB  |  Modified: {modified}")
        print()
    
    print("Options:")
    print("  all    - Delete all error documents")
    print("  1,2,3  - Delete specific documents (comma-separated)")
    print("  none   - Cancel")
    print()
    
    choice = input("Enter your choice: ").strip().lower()
    
    if choice == 'none' or not choice:
        print("❌ Cleanup cancelled")
        return
    
    # Determine which files to delete
    to_delete = []
    if choice == 'all':
        to_delete = error_files
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            to_delete = [error_files[i-1] for i in indices if 0 < i <= len(error_files)]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
    
    if not to_delete:
        print("❌ No files selected")
        return
    
    # Confirm deletion
    print(f"\n⚠️  About to delete {len(to_delete)} file(s):")
    for filepath in to_delete:
        rel_path = Path(filepath).relative_to(kb.base_path)
        print(f"  - {rel_path}")
    
    print()
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != 'DELETE':
        print("❌ Cleanup cancelled")
        return
    
    # Delete files
    deleted = 0
    failed = 0
    for filepath in to_delete:
        try:
            os.remove(filepath)
            deleted += 1
            print(f"✓ Deleted: {Path(filepath).relative_to(kb.base_path)}")
        except Exception as e:
            failed += 1
            print(f"✗ Failed: {Path(filepath).relative_to(kb.base_path)} - {e}")
    
    print(f"\n✅ Successfully deleted {deleted} file(s)")
    if failed > 0:
        print(f"⚠️  Failed to delete {failed} file(s)")
    
    # Regenerate index
    if deleted > 0:
        orchestrator = AgentOrchestrator(kb)
        orchestrator.maintainer_agent.create_index()
        print("✅ Index regenerated")

def cmd_categories(args):
    """List all categories"""
    print_header("Knowledge Base Categories")
    
    kb = KnowledgeBase()
    
    for category, description in kb.categories.items():
        cat_path = os.path.join(kb.base_path, category)
        count = 0
        if os.path.exists(cat_path):
            count = len([f for f in os.listdir(cat_path) if f.endswith('.md')])
        
        status = "✅" if count > 0 else "📝"
        print(f"{status} {category:20s} ({count:2d} docs) - {description}")

def cmd_outdated(args):
    """Find outdated documents"""
    days = int(args[0]) if len(args) > 0 else 30
    
    print_header(f"Documents Older Than {days} Days")
    
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    outdated = orchestrator.maintainer_agent.identify_outdated_docs(days=days)
    
    if not outdated:
        print(f"✅ No documents older than {days} days")
        return
    
    print(f"⚠️  Found {len(outdated)} outdated documents:\n")
    for i, filepath in enumerate(outdated, 1):
        rel_path = Path(filepath).relative_to(kb.base_path)
        from datetime import datetime
        mtime = os.path.getmtime(filepath)
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        print(f"{i:2d}. [{date_str}] {rel_path}")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "research": cmd_research,
        "search": cmd_search,
        "gaps": cmd_gaps,
        "index": cmd_index,
        "recent": cmd_recent,
        "stats": cmd_stats,
        "view": cmd_view,
        "categories": cmd_categories,
        "outdated": cmd_outdated,
        "help": lambda _: show_help(),
        "--help": lambda _: show_help(),
        "-h": lambda _: show_help(),
    }
    
    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print("Run './kb_cli.py help' for usage information")
        sys.exit(1)
    
    try:
        commands[command](args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
from kb_agent_system_claude import KnowledgeBase, AgentOrchestrator

def main():
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python kb_cli.py research '<topic>'")
        print("  python kb_cli.py search '<query>'")
        print("  python kb_cli.py gaps")
        print("  python kb_cli.py index")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "research":
        topic = sys.argv[2] if len(sys.argv) > 2 else "Midnight Blockchain"
        result = orchestrator.research_and_document(topic)
        print(f"\n✓ Created: {result['documentation_file']}")
        
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = kb.search(query)
        print(f"\nFound {len(results)} documents:")
        for r in results[:10]:  # Show first 10
            print(f"  - {r}")
            
    elif command == "gaps":
        gaps = orchestrator.analyze_and_plan()
        print(gaps)
        
    elif command == "index":
        index_file = orchestrator.maintainer_agent.create_index()
        print(f"✓ Index updated: {index_file}")
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
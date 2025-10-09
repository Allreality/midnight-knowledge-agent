"""
Midnight Knowledge Base Agent System
A multi-agent system for building and maintaining a comprehensive knowledge base
"""

import os
from datetime import datetime
from typing import List, Dict
import json

class KnowledgeBase:
    """Central knowledge repository"""
    
    def __init__(self, base_path: str = "./knowledge_base"):
        self.base_path = base_path
        self.categories = {
            "midnight": "Midnight blockchain documentation",
            "cardano": "Cardano technical specs",
            "healthcare": "Healthcare standards and regulations",
            "zkproofs": "Zero-knowledge proof research",
            "competitors": "Competitive analysis",
            "architecture": "System architecture and design",
            "smart_contracts": "Smart contract patterns and code",
            "research": "Raw research findings"
        }
        self._initialize_structure()
    
    def _initialize_structure(self):
        """Create folder structure for knowledge base"""
        for category in self.categories.keys():
            path = os.path.join(self.base_path, category)
            os.makedirs(path, exist_ok=True)
    
    def add_document(self, category: str, title: str, content: str, 
                     metadata: Dict = None) -> str:
        """Add a document to the knowledge base"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title.replace(' ', '_')}.md"
        filepath = os.path.join(self.base_path, category, filename)
        
        # Prepare document with metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            "created": datetime.now().isoformat(),
            "category": category,
            "title": title
        })
        
        # Write document
        with open(filepath, 'w') as f:
            f.write("---\n")
            f.write(json.dumps(doc_metadata, indent=2))
            f.write("\n---\n\n")
            f.write(f"# {title}\n\n")
            f.write(content)
        
        return filepath
    
    def search(self, query: str, category: str = None) -> List[str]:
        """Search for documents matching query"""
        results = []
        search_path = os.path.join(self.base_path, category) if category else self.base_path
        
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append(filepath)
        
        return results


class ResearchCuratorAgent:
    """Agent responsible for gathering and curating research"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "Research Curator"
    
    def research_topic(self, topic: str, sources: List[str]) -> Dict:
        """
        Research a topic from multiple sources
        In production, this would use web scraping, APIs, etc.
        """
        print(f"[{self.name}] Researching: {topic}")
        
        # Placeholder for actual research logic
        # In reality, this would:
        # - Query GitHub APIs
        # - Scrape documentation sites
        # - Search academic papers
        # - Monitor forums and social media
        
        findings = {
            "topic": topic,
            "sources_checked": sources,
            "summary": f"Research findings on {topic}",
            "key_points": [
                "Point 1 from source A",
                "Point 2 from source B",
                "Point 3 from source C"
            ],
            "raw_data": {
                "source1": "Raw data from source 1",
                "source2": "Raw data from source 2"
            }
        }
        
        return findings
    
    def save_research(self, findings: Dict) -> str:
        """Save research findings to knowledge base"""
        content = f"""
## Summary
{findings['summary']}

## Key Points
"""
        for point in findings['key_points']:
            content += f"- {point}\n"
        
        content += "\n## Sources Checked\n"
        for source in findings['sources_checked']:
            content += f"- {source}\n"
        
        content += "\n## Raw Data\n"
        for source, data in findings['raw_data'].items():
            content += f"\n### {source}\n{data}\n"
        
        filepath = self.kb.add_document(
            category="research",
            title=findings['topic'],
            content=content,
            metadata={
                "agent": self.name,
                "sources": findings['sources_checked']
            }
        )
        
        print(f"[{self.name}] Research saved to: {filepath}")
        return filepath


class DocumentationWriterAgent:
    """Agent responsible for creating clean documentation"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "Documentation Writer"
    
    def synthesize_documentation(self, research_files: List[str], 
                                  doc_type: str = "guide") -> Dict:
        """
        Take raw research and create polished documentation
        In production, this would use Claude API or similar
        """
        print(f"[{self.name}] Synthesizing documentation from {len(research_files)} sources")
        
        # Placeholder for actual synthesis logic
        # In reality, this would:
        # - Read research files
        # - Use LLM to synthesize information
        # - Format in appropriate style
        # - Generate diagrams if needed
        
        documentation = {
            "title": "Midnight Privacy Features Overview",
            "type": doc_type,
            "content": """
## Introduction
Midnight is a privacy-focused blockchain that uses zero-knowledge proofs...

## Key Features
### Zero-Knowledge Proofs
Midnight implements ZK-proofs to enable...

### Dual Token System
The NIGHT and DUST token model provides...

## Technical Architecture
[Diagram placeholder]

## Use Cases
1. Healthcare data privacy
2. Supply chain verification
3. Identity management

## References
- [Research file 1]
- [Research file 2]
""",
            "category": "midnight"
        }
        
        return documentation
    
    def publish_documentation(self, doc: Dict) -> str:
        """Publish documentation to knowledge base"""
        filepath = self.kb.add_document(
            category=doc['category'],
            title=doc['title'],
            content=doc['content'],
            metadata={
                "agent": self.name,
                "type": doc['type']
            }
        )
        
        print(f"[{self.name}] Documentation published to: {filepath}")
        return filepath


class KnowledgeBaseMaintainerAgent:
    """Agent responsible for organizing and maintaining the KB"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "KB Maintainer"
    
    def create_index(self) -> str:
        """Create an index of all documents"""
        print(f"[{self.name}] Creating knowledge base index")
        
        index_content = "# Knowledge Base Index\n\n"
        
        for category, description in self.kb.categories.items():
            index_content += f"## {category.title()}\n"
            index_content += f"*{description}*\n\n"
            
            category_path = os.path.join(self.kb.base_path, category)
            files = [f for f in os.listdir(category_path) if f.endswith('.md')]
            
            if files:
                for file in sorted(files):
                    # Extract title from filename
                    title = file.replace('.md', '').replace('_', ' ')
                    rel_path = f"{category}/{file}"
                    index_content += f"- [{title}]({rel_path})\n"
            else:
                index_content += "*No documents yet*\n"
            
            index_content += "\n"
        
        # Save index
        index_path = os.path.join(self.kb.base_path, "INDEX.md")
        with open(index_path, 'w') as f:
            f.write(index_content)
        
        print(f"[{self.name}] Index created at: {index_path}")
        return index_path
    
    def add_cross_references(self, doc_path: str) -> None:
        """Add links between related documents"""
        print(f"[{self.name}] Adding cross-references to: {doc_path}")
        
        # Placeholder for cross-referencing logic
        # In reality, this would:
        # - Analyze document content
        # - Find related documents
        # - Add appropriate links
        # - Update backlinks
        
        pass
    
    def identify_outdated_docs(self, days: int = 30) -> List[str]:
        """Find documents that might need updating"""
        print(f"[{self.name}] Checking for outdated documents (>{days} days old)")
        
        outdated = []
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.kb.base_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_date:
                        outdated.append(filepath)
        
        print(f"[{self.name}] Found {len(outdated)} potentially outdated documents")
        return outdated


class AgentOrchestrator:
    """Coordinates the agents to work together"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.research_agent = ResearchCuratorAgent(knowledge_base)
        self.doc_agent = DocumentationWriterAgent(knowledge_base)
        self.maintainer_agent = KnowledgeBaseMaintainerAgent(knowledge_base)
    
    def research_and_document(self, topic: str, sources: List[str]) -> Dict:
        """
        Complete workflow: research -> document -> organize
        """
        print(f"\n{'='*60}")
        print(f"Starting research and documentation workflow for: {topic}")
        print(f"{'='*60}\n")
        
        # Step 1: Research
        findings = self.research_agent.research_topic(topic, sources)
        research_file = self.research_agent.save_research(findings)
        
        # Step 2: Create documentation
        doc = self.doc_agent.synthesize_documentation([research_file])
        doc_file = self.doc_agent.publish_documentation(doc)
        
        # Step 3: Update index
        index_file = self.maintainer_agent.create_index()
        
        print(f"\n{'='*60}")
        print(f"Workflow complete!")
        print(f"{'='*60}\n")
        
        return {
            "research_file": research_file,
            "documentation_file": doc_file,
            "index_file": index_file
        }


# Example usage
if __name__ == "__main__":
    # Initialize the system
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    # Run a research and documentation workflow
    result = orchestrator.research_and_document(
        topic="Midnight Privacy Features",
        sources=[
            "https://midnight.network/docs",
            "https://github.com/input-output-hk/midnight",
            "Midnight whitepaper"
        ]
    )
    
    print("\nFiles created:")
    for key, filepath in result.items():
        print(f"  {key}: {filepath}")
    
    # Check for outdated documents
    print("\n" + "="*60)
    outdated = orchestrator.maintainer_agent.identify_outdated_docs(days=7)
    
    # Search example
    print("\n" + "="*60)
    print("Searching for 'privacy'...")
    results = kb.search("privacy")
    print(f"Found {len(results)} documents mentioning 'privacy'")
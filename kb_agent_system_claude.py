# File: kb_agent_system_claude.py
# Path: ~/knowledgeagent/kb_agent_system_claude.py
# Description: Multi-agent system for Midnight blockchain research and documentation
# Author: [Akil Hashim]
# Created: 2025-01-06
# Python: 3.x
# Dependencies: anthropic, markdown

"""
Multi-Agent Knowledge Base System for Midnight Blockchain

This system coordinates three agents:
1. Research Curator - Gathers information
2. Documentation Writer - Synthesizes documentation
3. KB Maintainer - Manages knowledge base
"""

import anthropic
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"
RESEARCH_DIR = KB_DIR / "research"
DOCS_DIR = KB_DIR / "midnight"
MODEL_NAME = "claude-3-5-haiku-20241022"
MAX_TOKENS = 4096

# Initialize Claude API - ONLY ONCE
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
    print("Please set it in your .env file or export it:")
    print("  export ANTHROPIC_API_KEY='your-key-here'")
    sys.exit(1)

try:
    client = anthropic.Anthropic(api_key=api_key)
    print(f"✓ Anthropic client initialized successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize Anthropic client: {e}")
    sys.exit(1)


def save_with_header(content, filepath, agent_name, status="Success"):
    """Save file with standardized header"""
    header = f"""<!-- File: {filepath.name} -->
<!-- Path: {filepath.relative_to(BASE_DIR)} -->
<!-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
<!-- Agent: {agent_name} -->
<!-- Status: {status} -->

"""
    with open(filepath, 'w') as f:
        f.write(header + content)


def test_api_connection():
    """Test the API connection before running the main workflow"""
    print("\n" + "="*60)
    print("Testing API Connection...")
    print("="*60 + "\n")
    
    try:
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in environment variables")
            return False
        
        print(f"✓ API Key found (length: {len(api_key)})")
        
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        print(f"✓ API connection successful")
        print(f"✓ Model: {MODEL_NAME}")
        print(f"✓ Response received")
        return True
        
    except anthropic.APIConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify API endpoint is accessible")
        return False
        
    except anthropic.APIStatusError as e:
        print(f"❌ API Status Error: {e.status_code}")
        print(f"   Message: {e.message}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
        return False


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
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title.replace(' ', '_')}.md"
        filepath = os.path.join(self.base_path, category, filename)
        
        doc_metadata = metadata or {}
        doc_metadata.update({
            "created": datetime.now().isoformat(),
            "category": category,
            "title": title
        })
        
        with open(filepath, 'w') as f:
            f.write("---\n")
            f.write(json.dumps(doc_metadata, indent=2))
            f.write("\n---\n\n")
            f.write(f"# {title}\n\n")
            f.write(content)
        
        return filepath
    
    def get_document(self, filepath: str) -> str:
        """Read a document from the knowledge base"""
        with open(filepath, 'r') as f:
            return f.read()
    
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
    """Agent responsible for gathering and curating research with Claude"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "Research Curator"
    
    def research_topic(self, topic: str, context: str = "") -> Dict:
        """Research a topic using Claude's knowledge"""
        print(f"[{self.name}] Researching: {topic}")
        
        prompt = f"""You are a research agent for a blockchain infrastructure project focusing on Midnight (privacy-preserving blockchain on Cardano).

Research Topic: {topic}

{f"Additional Context: {context}" if context else ""}

Please provide:
1. A comprehensive summary of this topic
2. Key points and important details
3. Technical specifications if applicable
4. Relevant use cases or applications
5. Any concerns or limitations
6. Sources or references (even if general)

Format your response as structured research findings."""

        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            research_content = message.content[0].text
            
            findings = {
                "topic": topic,
                "summary": research_content,
                "researched_by": MODEL_NAME,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[{self.name}] Research complete ({len(research_content)} chars)")
            return findings
            
        except Exception as e:
            print(f"[{self.name}] Error during research: {e}")
            return {
                "topic": topic,
                "summary": f"Research on {topic} (API Error: {str(e)})",
                "researched_by": "Fallback",
                "timestamp": datetime.now().isoformat()
            }
    
    def save_research(self, findings: Dict) -> str:
        """Save research findings to knowledge base"""
        content = findings['summary']
        
        filepath = self.kb.add_document(
            category="research",
            title=findings['topic'],
            content=content,
            metadata={
                "agent": self.name,
                "researched_by": findings.get('researched_by', 'Unknown'),
                "timestamp": findings.get('timestamp', datetime.now().isoformat())
            }
        )
        
        print(f"[{self.name}] Research saved to: {filepath}")
        return filepath

# Add this method to DocumentationWriterAgent in kb_agent_system_claude.py
# Right after the __init__ method (around line 350)

def _detect_category(self, topic: str, context: str, source_url: str = "") -> str:
    """Smart category detection"""
    combined_text = f"{topic} {context} {source_url}".lower()
    
    # Simple keyword matching
    if any(word in combined_text for word in ['cardano', 'ada', 'plutus', 'stake pool']):
        return 'cardano'
    elif any(word in combined_text for word in ['healthcare', 'health', 'hipaa', 'fhir', 'medical']):
        return 'healthcare'
    elif any(word in combined_text for word in ['zero knowledge', 'zk-', 'zkp', 'proof']):
        return 'zkproofs'
    elif any(word in combined_text for word in ['smart contract', 'solidity', 'contract']):
        return 'smart_contracts'
    elif any(word in combined_text for word in ['architecture', 'design', 'system', 'infrastructure']):
        return 'architecture'
    else:
        return 'midnight'

class DocumentationWriterAgent:
    """Agent responsible for creating clean documentation with Claude"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "Documentation Writer"
    
    def _call_claude_with_retry(self, prompt: str, max_retries: int = 3):
        """Call Claude API with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                response = client.messages.create(
                    model=MODEL_NAME,
                    max_tokens=MAX_TOKENS,
                    temperature=0.7,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return response
                
            except anthropic.APIConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[{self.name}] Connection failed. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
                    
            except anthropic.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"[{self.name}] Rate limited. Waiting {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
    
    def synthesize_documentation(self, research_files: List[str], 
                                  doc_type: str = "guide",
                                  target_audience: str = "developers") -> Dict:
        """Take raw research and create polished documentation using Claude"""
        print(f"[{self.name}] Synthesizing documentation from {len(research_files)} sources")
        
        try:
            # Read all research files
            research_content = []
            for file_path in research_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        research_content.append(f"## Source: {file_path}\n\n{content}\n\n")
                except Exception as e:
                    print(f"[{self.name}] Warning: Could not read {file_path}: {e}")
            
            if not research_content:
                raise ValueError("No research content available to synthesize")
            
            combined_research = "\n".join(research_content)
            
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
                "category": "midnight",
                "written_by": MODEL_NAME,
                "sources": research_files,
                "model": response.model
            }
            
        except Exception as e:
            print(f"[{self.name}] Error creating documentation: {e}")
            return self._create_error_fallback(research_files, str(e))
    
    def _create_error_fallback(self, research_files: List[str], error_msg: str) -> Dict:
        """Create a basic documentation file when API fails"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        fallback_content = f"""# Documentation Generation Failed

**Error:** {error_msg}
**Timestamp:** {timestamp}

## Research Sources

The following research was collected but could not be synthesized due to an error:

"""
        
        for file_path in research_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    fallback_content += f"\n---\n\n### Source: {file_path}\n\n{content}\n\n"
            except Exception as e:
                fallback_content += f"\n- Could not read {file_path}: {e}\n"
        
        fallback_content += "\n---\n\n*Please check your API configuration and try again.*\n"
        
        return {
            "title": "Documentation (Error)",
            "type": "error",
            "content": fallback_content,
            "category": "midnight",
            "written_by": "Fallback",
            "error": error_msg
        }
    
    def publish_documentation(self, doc: Dict) -> str:
        """Publish documentation to knowledge base"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filepath = self.kb.add_document(
            category=doc['category'],
            title=doc['title'],
            content=doc['content'],
            metadata={
                "agent": self.name,
                "type": doc['type'],
                "written_by": doc.get('written_by', 'Unknown'),
                "sources": doc.get('sources', []),
                "created_at": timestamp
            }
        )
        
        print(f"[{self.name}] Documentation published to: {filepath}")
        return filepath


class KnowledgeBaseMaintainerAgent:
    """Agent responsible for organizing and maintaining the KB with Claude"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.name = "KB Maintainer"
    
    def create_index(self) -> str:
        """Create an index of all documents"""
        print(f"[{self.name}] Creating knowledge base index")
        
        index_content = "# Knowledge Base Index\n\n"
        index_content += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        total_docs = 0
        
        for category, description in self.kb.categories.items():
            index_content += f"## {category.title()}\n"
            index_content += f"*{description}*\n\n"
            
            category_path = os.path.join(self.kb.base_path, category)
            files = [f for f in os.listdir(category_path) if f.endswith('.md')]
            
            if files:
                total_docs += len(files)
                for file in sorted(files, reverse=True):
                    title = file.replace('.md', '').replace('_', ' ')
                    rel_path = f"{category}/{file}"
                    index_content += f"- [{title}]({rel_path})\n"
            else:
                index_content += "*No documents yet*\n"
            
            index_content += "\n"
        
        index_content += f"\n---\n**Total Documents: {total_docs}**\n"
        
        index_path = os.path.join(self.kb.base_path, "INDEX.md")
        with open(index_path, 'w') as f:
            f.write(index_content)
        
        print(f"[{self.name}] Index created at: {index_path} ({total_docs} documents)")
        return index_path
    
    def analyze_knowledge_gaps(self) -> str:
        """Use Claude to identify gaps in documentation"""
        print(f"[{self.name}] Analyzing knowledge gaps...")
        
        index_path = os.path.join(self.kb.base_path, "INDEX.md")
        try:
            with open(index_path, 'r') as f:
                index_content = f.read()
        except:
            index_content = "No index available"
        
        prompt = f"""You are analyzing a knowledge base for a Midnight blockchain infrastructure project.

Current Knowledge Base Index:
{index_content}

Please identify:
1. Important topics that are missing or underdocumented
2. Areas that need more depth
3. Topics that should be added for completeness
4. Suggested priorities for new documentation

Focus on: Midnight blockchain, privacy features, healthcare applications, zero-knowledge proofs, smart contracts, and infrastructure.

Provide a prioritized list of gaps and recommendations."""

        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            analysis = message.content[0].text
            print(f"[{self.name}] Gap analysis complete")
            
            # Save analysis as a document
            self.kb.add_document(
                category="architecture",
                title="Knowledge Base Gap Analysis",
                content=analysis,
                metadata={
                    "agent": self.name,
                    "type": "analysis"
                }
            )
            
            return analysis
            
        except Exception as e:
            print(f"[{self.name}] Error analyzing gaps: {e}")
            return f"Error analyzing gaps: {e}"
    
    def identify_outdated_docs(self, days: int = 30) -> List[str]:
        """Find documents that might need updating"""
        print(f"[{self.name}] Checking for outdated documents (>{days} days old)")
        
        outdated = []
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.kb.base_path):
            for file in files:
                if file.endswith('.md') and file != 'INDEX.md':
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
    
    def research_and_document(self, topic: str, context: str = "", 
                             doc_type: str = "guide",
                             target_audience: str = "developers") -> Dict:
        """Complete workflow: research -> document -> organize"""
        print(f"\n{'='*60}")
        print(f"Starting research and documentation workflow")
        print(f"Topic: {topic}")
        print(f"{'='*60}\n")
        
        # Step 1: Research with Claude
        findings = self.research_agent.research_topic(topic, context)
        research_file = self.research_agent.save_research(findings)
        
        # Step 2: Create documentation with Claude
        doc = self.doc_agent.synthesize_documentation(
            [research_file], 
            doc_type=doc_type,
            target_audience=target_audience
        )
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
    
    def analyze_and_plan(self):
        """Analyze knowledge base and suggest next topics"""
        print(f"\n{'='*60}")
        print(f"Analyzing knowledge base...")
        print(f"{'='*60}\n")
        
        gaps = self.maintainer_agent.analyze_knowledge_gaps()
        return gaps

# Main execution
if __name__ == "__main__":
    # Test connection first
    if not test_api_connection():
        print("\n⚠️  API connection test failed. Please fix the issues above before continuing.")
        sys.exit(1)
    
    # Initialize system
    kb = KnowledgeBase()
    orchestrator = AgentOrchestrator(kb)
    
    # Example 1: Research and document a topic
    result = orchestrator.research_and_document(
        topic="Midnight Zero-Knowledge Proofs Implementation",
        context="Focus on how Midnight uses ZK-proofs for privacy-preserving healthcare data",
        doc_type="technical guide",
        target_audience="blockchain developers"
    )
    
    print("\nFiles created:")
    for key, filepath in result.items():
        print(f"  {key}: {filepath}")
    
    # Example 2: Analyze knowledge gaps
    print("\n" + "="*60)
    gaps = orchestrator.analyze_and_plan()
    
    # Example 3: Check for outdated docs
    print("\n" + "="*60)
    outdated = orchestrator.maintainer_agent.identify_outdated_docs(days=7)
    
    # Example 4: Search
    print("\n" + "="*60)
    print("Searching for 'privacy'...")
    results = kb.search("privacy")
    print(f"Found {len(results)} documents mentioning 'privacy'")

# END OF FILE - Nothing should be after this!
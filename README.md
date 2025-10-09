cat > README.md << 'EOF'
# 🧠 Knowledge Base Multi-Agent System

An intelligent, autonomous research and documentation system powered by Claude AI for blockchain infrastructure knowledge management.

![Dashboard](https://img.shields.io/badge/Dashboard-Dark_Mode-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Latest-black?style=for-the-badge&logo=flask)
![Claude](https://img.shields.io/badge/Claude-AI-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview

This system coordinates three intelligent agents to build and maintain a comprehensive knowledge base about Midnight blockchain, Cardano, healthcare applications, and privacy-preserving technologies.

### Key Features

- 🤖 **Multi-Agent Architecture** - Coordinated AI agents working together
- 🌐 **Web Dashboard** - Beautiful dark-mode interface for monitoring and control
- 📊 **Real-time Stats** - Live tracking of documents, tasks, and knowledge growth
- 🔍 **Intelligent Search** - Full-text search across your entire knowledge base
- 📝 **Auto-Documentation** - AI generates clean, structured documentation
- 🎨 **Source Tracking** - Support for webpages, YouTube, Medium, and manual research
- ✅ **Approval Workflow** - Review and approve research tasks before processing
- 📈 **Gap Analysis** - AI identifies missing topics and recommends priorities

## 🏗️ Architecture

### 🤖 Three Specialized AI Agents

1. **Research Curator** - Gathers and analyzes information on blockchain topics
2. **Documentation Writer** - Synthesizes research into comprehensive technical documentation
3. **KB Maintainer** - Organizes, indexes, and maintains the knowledge base

### The Three Agents

┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
└──────────────────────┬───────────────────────────────────────┘
│
┌──────────────┼──────────────┐
▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Research    │ │Documentation  │ │      KB       │
│   Curator     │ │    Writer     │ │  Maintainer   │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
│                 │                 │
▼                 ▼                 ▼
Research Files    Documentation     Index & Analysis

#### 1. Research Curator Agent 🔬
- Gathers information on specified topics
- Uses Claude AI for deep research
- Saves raw findings to knowledge base
- Tracks sources and metadata

#### 2. Documentation Writer Agent ✍️
- Synthesizes research into clean documentation
- Creates structured, readable guides
- Includes code examples and best practices
- Formats in beautiful Markdown

#### 3. KB Maintainer Agent 📚
- Organizes and indexes all documents
- Identifies knowledge gaps
- Tracks outdated content
- Maintains category structure

### 🌐 Web Dashboard

- **Real-time monitoring** of research tasks and knowledge base stats
- **Task approval workflow** - Review and approve research before processing
- **Source integration** - Direct agents to webpages, YouTube videos, or Medium articles
- **Dark mode interface** - Beautiful, modern UI optimized for long sessions
- **Document viewer** - Read generated documentation with syntax highlighting
- **Search functionality** - Full-text search across all documents

### 📊 Knowledge Management

- **Automatic categorization** - Smart detection of document categories
- **Progress tracking** - Visual progress bars for each category
- **Gap analysis** - AI-powered identification of missing topics
- **Version control** - Complete history of all generated content
- **Export capabilities** - Generate HTML, Markdown, or PDF outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key (Claude)
- 2GB free disk space

# Required packages
pip install anthropic flask markdown2 python-dotenv

### Installation

# Clone the repository
git clone https://github.com/allreality/midnight-knowledge-agent.git
cd knowledge-agent-system

# Install dependencies
pip install -r requirements.txt

# Set up your API key
echo "ANTHROPIC_API_KEY='your-key-here'" > .env

# Initialize the knowledge base
python kb_agent_system_claude.py

Launch Web Dashboard

python web_dashboard.py

```bash
# 1. Clone or create project directory if it is not already their
mkdir ~/knowledgeagent
cd ~/knowledgeagent

# 2. Create virtual environment
python -m venv trading-bot-env
source trading-bot-env/bin/activate  # On Windows: trading-bot-env\Scripts\activate

# 3. Install dependencies
pip install anthropic flask flask-cors markdown2 python-dotenv

# 4. Set up environment variables
echo "ANTHROPIC_API_KEY='your-api-key-here'" > .env

# 5. Create directory structure
mkdir -p knowledge_base/{research,midnight,cardano,healthcare,zkproofs,architecture,smart_contracts,competitors}
mkdir -p templates static/css static/js

Files Setup
Copy the following files into your project:

kb_agent_system_claude.py - Main agent system
web_dashboard.py - Web interface
kb_cli.py - Command-line interface
templates/dashboard.html - Dashboard UI
static/css/dashboard.css - Dark mode styles
static/js/dashboard.js - Frontend logic

🎮 Usage
Start the Web Dashboard
python web_dashboard.py

Then open: http://localhost:5000
Command-Line Interface

# Research a topic
./kb_cli.py research "Midnight Smart Contracts"

# Research with context
./kb_cli.py research "Zero-Knowledge Proofs" "Focus on healthcare applications"

# Search knowledge base
./kb_cli.py search "privacy"

# Show statistics
./kb_cli.py stats

# List recent documents
./kb_cli.py recent midnight 10

# Find outdated docs
./kb_cli.py outdated 30

# View categories
./kb_cli.py categories

# Analyze knowledge gaps
./kb_cli.py gaps

Direct Python Usage
from kb_agent_system_claude import KnowledgeBase, AgentOrchestrator

# Initialize
kb = KnowledgeBase()
orchestrator = AgentOrchestrator(kb)

# Research and document a topic
result = orchestrator.research_and_document(
    topic="Midnight Zero-Knowledge Proofs",
    context="Focus on healthcare privacy applications",
    doc_type="technical guide",
    target_audience="developers"
)

print(f"Documentation: {result['documentation_file']}")
print(f"Research: {result['research_file']}")

# Search knowledge base
results = kb.search("privacy")
print(f"Found {len(results)} documents")

# Analyze gaps
gaps = orchestrator.analyze_and_plan()
print(gaps)

Open your browser to: http://localhost:5000
📖 Usage Guide
Creating Research Tasks

Click "New Task" in the dashboard
Fill in details:

Topic: The main research subject
Context: Additional focus areas or constraints
Source Type: Manual, Webpage, YouTube, or Medium
Source URL: Direct the agent to specific content


Click "Create" - Task enters pending state

Approving and Processing

Navigate to "Research Queue"
Review task details
Click "Approve" to start research
Watch status change: pending → processing → completed
View generated documentation when complete

Using the CLI

# Research a topic
./kb_cli.py research "Midnight Smart Contracts"

# Search the knowledge base
./kb_cli.py search "privacy"

# View statistics
./kb_cli.py stats

# Show recent documents
./kb_cli.py recent midnight 10

# Find outdated documents
./kb_cli.py outdated 30

# Run gap analysis
./kb_cli.py gaps

🏗️ Architecture
Agent Workflow

User Input → Research Curator → Documentation Writer → KB Maintainer → Knowledge Base
              ↓                    ↓                     ↓
         [Claude API]        [Claude API]          [File System]

Directory Structure
knowledge-agent-system/
├── knowledge_base/          # Generated knowledge base
│   ├── midnight/           # Midnight blockchain docs
│   ├── cardano/            # Cardano technical specs
│   ├── healthcare/         # Healthcare standards
│   ├── zkproofs/           # Zero-knowledge proofs
│   ├── research/           # Raw research findings
│   ├── architecture/       # System architecture
│   └── INDEX.md            # Master index
├── templates/              # Web dashboard templates
│   └── dashboard.html
├── static/                 # CSS and JavaScript
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
├── kb_agent_system_claude.py  # Main agent system
├── web_dashboard.py            # Flask web server
├── kb_cli.py                   # Command-line interface
└── README.md

🎯 Use Cases
Blockchain Development

Research consensus mechanisms
Compare smart contract platforms
Analyze privacy technologies
Study token economics

Healthcare Integration

Track HIPAA compliance requirements
Document HL7/FHIR standards
Research privacy regulations
Analyze healthcare blockchain solutions

Competitive Analysis

Monitor competing projects
Track technology trends
Identify partnership opportunities
Benchmark features

Team Knowledge Building

Create onboarding documentation
Maintain technical specifications
Build institutional knowledge
Reduce knowledge silos

🔧 Configuration
Environment Variables

# .env file
ANTHROPIC_API_KEY=your-api-key-here
MODEL_NAME=claude-3-5-haiku-20241022  # Optional
MAX_TOKENS=4096                       # Optional

Category Customization
Edit kb_agent_system_claude.py:

self.categories = {
    "midnight": "Midnight blockchain documentation",
    "cardano": "Cardano technical specs",
    "healthcare": "Healthcare standards",
    "your_category": "Your description",
}

Agent Prompts
Customize agent behavior by modifying prompts in:

ResearchCuratorAgent.research_topic()
DocumentationWriterAgent.synthesize_documentation()
KnowledgeBaseMaintainerAgent.analyze_knowledge_gaps()

📊 Dashboard Features
Overview

Real-time stats - Documents, tasks, storage
Recent documents - Quick access to latest research
Category breakdown - Visual progress indicators
Auto-refresh - Updates every 30 seconds

Research Queue

Status tracking - Pending, processing, completed, denied
Approve/Deny - Manual review before processing
Source links - Direct access to reference materials
Delete capability - Remove unwanted tasks

Documents

Browse all documents - Organized by category
View in modal - Formatted markdown display
Metadata display - Creation date, size, author

Search

Full-text search - Search across all documents
Preview snippets - Context around matches
Click to view - Open full document

🔬 Advanced Features
Batch Research
Create multiple tasks programmatically:

import requests

topics = [
    "Midnight Network Architecture",
    "Cardano Plutus Contracts",
    "Healthcare Blockchain Privacy"
]

for topic in topics:
    requests.post('http://localhost:5000/api/tasks', json={
        'topic': topic,
        'context': 'Technical deep dive',
        'source_type': 'manual',
        'source_url': ''
    })
Scheduled Updates
Set up cron job for daily research:
# crontab -e
0 9 * * * cd ~/knowledge-agent-system && python daily_research.py

Export Knowledge Base
# Export to HTML
python export_kb.py --format html --output ./kb_export

# Export specific category
python export_kb.py --category midnight --format pdf

🛡️ Security Considerations

API Key Protection - Never commit .env files
Rate Limiting - Exponential backoff on API calls
Input Validation - Sanitize all user inputs
Human Oversight - Review before approving tasks
Access Control - Run dashboard behind authentication in production

🐛 Troubleshooting
API Connection Errors

# Test API connection
python -c "from kb_agent_system_claude import test_api_connection; test_api_connection()"

# Check API key
echo $ANTHROPIC_API_KEY

Dashboard Not Loading
# Check if templates exist
ls templates/dashboard.html

# Verify static files
ls static/css/dashboard.css static/js/dashboard.js

# Check Flask is running
lsof -i :5000

Tasks Stuck in Processing
# Check terminal for errors
# Look for API rate limits or connection issues

# Restart the server
pkill -f web_dashboard.py
python web_dashboard.py

📈 Performance

Average research time: 30-60 seconds per task
Token usage: ~2000-4000 tokens per research task
Concurrent tasks: Supports parallel processing
Storage: ~5-10 KB per document

## 🔐 Security & Privacy

**Important Notes:**
- ⚠️ **Never commit your `.env` file** containing API keys
- 🔒 Store sensitive data outside the repository
- 🛡️ Run dashboard behind authentication for production use
- 📝 Review all AI-generated content before publishing
- 🚫 This system makes API calls - be aware of rate limits and costs

## 💰 Cost Considerations

Approximate costs using Claude 3.5 Haiku:
- **Per research task:** ~$0.01-0.05 USD
- **Daily usage (10 tasks):** ~$0.10-0.50 USD
- **Monthly (300 tasks):** ~$3-15 USD

Monitor your usage at: https://console.anthropic.com/

## ⚠️ Disclaimer

This is an **unofficial, educational project** for learning and research purposes. 

- Not affiliated with or endorsed by Midnight, Cardano, or Input Output
- AI-generated content should be reviewed and verified
- No warranty provided - use at your own risk
- Cryptocurrency investments are risky - this is not financial advice

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/screenshots/dashboard.png)

### Research Queue
![Research Queue](docs/screenshots/queue.png)

### Document Viewer
![Document Viewer](docs/screenshots/viewer.png)

🗺️ Roadmap

 Multi-user support with authentication
 Integration with Obsidian/Notion
 Automated daily research schedules
 Email/Slack notifications for completed tasks
 Advanced filtering and tagging
 Knowledge graph visualization
 Export to Confluence/GitBook
 API endpoints for external integrations

🤝 Contributing
Contributions welcome! Please:

Fork the repository
Create a feature branch
Make your changes
Add tests
Submit a pull request

📄 License
MIT License - see LICENSE file for details
🙏 Acknowledgments

Built with Claude by Anthropic
UI inspired by modern dashboard designs
Community feedback and contributions

📞 Support

Issues: GitHub Issues
Discussions: GitHub Discussions
Email: akilhashim1@gmail.com

🎓 Learn More

Midnight Blockchain Docs
Cardano Developer Portal
Claude API Documentation

Built with ❤️ for the Midnight and Cardano ecosystems
EOF


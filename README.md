# 🧠 MindWeave - AI-Powered Personal Knowledge Graph

Transform your documents into an intelligent, interconnected knowledge network. MindWeave uses AI to extract entities, discover relationships, and enable semantic search across your personal knowledge base.

![MindWeave Demo](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 📄 **Multi-Format Support** - Upload PDF, DOCX, Markdown, and TXT files
- 🤖 **AI Entity Extraction** - Automatically extract people, concepts, technologies, and organizations using GPT-4o-mini
- 🔗 **Relationship Mapping** - Discover connections between concepts with AI-powered relationship detection
- 🔍 **Semantic Search** - Find documents by meaning, not just keywords, using OpenAI embeddings
- 🧩 **Multi-Hop Reasoning** - Connect distant concepts through intelligent graph traversal
- 📊 **Knowledge Graph** - Visualize your knowledge as an interconnected network in Neo4j
- 💰 **Cost-Effective** - Built with GPT-4o-mini, stays under $5 for typical use cases

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                        │
└─────────────────────────────────────────────────────────────┘
│
┌───────────────────┼───────────────────┐
│                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│   PostgreSQL   │  │    Neo4j    │  │    ChromaDB     │
│   (Metadata)   │  │   (Graph)   │  │   (Vectors)     │
└────────────────┘  └─────────────┘  └─────────────────┘
│
┌───────▼───────┐
│  OpenAI API   │
│  GPT-4o-mini  │
└───────────────┘

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- OpenAI API Key
- 2GB RAM minimum

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mindweave.git
cd mindweave
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file in the root directory
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Start databases with Docker**
```bash
docker-compose up -d
```

6. **Run the application**
```bash
streamlit run AI/ui/streamlit_app.py
```

7. **Access the application**
Open your browser to: http://localhost:8501

## 📦 Project Structure
mindweave/
├── AI/
│   ├── config/              # Configuration and settings
│   │   └── settings.py
│   ├── extraction/          # Entity and relationship extraction
│   │   ├── entity_extractor.py
│   │   └── relationship_mapper.py
│   ├── graph/               # Neo4j graph operations
│   │   └── builder.py
│   ├── ingest/              # Document parsing and preprocessing
│   │   ├── parsers.py
│   │   ├── preprocessor.py
│   │   └── embeddings.py
│   ├── prompts/             # AI prompts for extraction
│   │   ├── entity_extraction.py
│   │   └── relationships.py
│   ├── reasoning/           # Multi-hop reasoning engine
│   │   ├── query_engine.py
│   │   └── ai_reasoner.py
│   ├── storage/             # Database interfaces
│   │   ├── metadata_store.py
│   │   └── vector_store.py
│   └── ui/                  # Streamlit interface
│       └── streamlit_app.py
├── data/                    # Data storage
│   ├── uploads/             # Uploaded documents
│   └── chroma/              # ChromaDB vector store
├── docker-compose.yml       # Docker configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md

## 🎯 Usage

### 1. Upload Documents
- Navigate to **Upload** tab
- Select PDF, DOCX, MD, or TXT files
- Enable "Extract entities" for AI processing
- Click **Process Files**

### 2. Explore Your Knowledge Graph
- Go to **Documents** tab
- View extracted entities and relationships
- See connections between concepts

### 3. Semantic Search
- Navigate to **Search** tab
- Enter natural language queries
- Find documents by meaning, not keywords
- Example: "machine learning projects" finds relevant docs even without exact matches

### 4. Multi-Hop Reasoning
- Go to **Reasoning** tab
- **Ask Questions**: "What technologies does [person] work with?"
- **Find Path**: Connect two entities through the graph
- **Explore Entity**: See all connections for a concept
- **Common Ground**: Find bridges between entities

## 💡 Example Use Cases

### Personal Knowledge Management
- Upload your notes, resumes, and research papers
- Discover connections between your interests
- Search your entire knowledge base semantically

### Research Organization
- Process academic papers and articles
- Extract key concepts and authors
- Find relationships between research topics

### Professional Development
- Track skills and technologies you've learned
- Map relationships between projects and tools
- Answer questions about your experience

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenAI
OPENAI_API_KEY=your_key_here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mindweave123

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mindweave
POSTGRES_USER=mindweave_user
POSTGRES_PASSWORD=mindweave123

# ChromaDB
CHROMA_PATH=./data/chroma

# Cost Limits
COST_LIMIT=5.0
WARN_AT_COST=4.0
```

### Database Configuration

**Neo4j (Graph Database)**
- URL: http://localhost:7474
- Username: neo4j
- Password: mindweave123

**PostgreSQL (Metadata)**
- Host: localhost:5432
- Database: mindweave
- Username: mindweave_user

## 📊 Cost Breakdown

Using GPT-4o-mini for AI processing:

| Operation | Cost per Document | Tokens |
|-----------|------------------|---------|
| Entity Extraction | ~$0.01 | ~5K tokens |
| Relationship Mapping | ~$0.001 | ~500 tokens |
| Embeddings | ~$0.0001 | ~1K tokens |
| Question Answering | ~$0.002 | ~1K tokens |

**Total: ~$0.50 for 10 documents** (well under $5 budget!)

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4o-mini, text-embedding-3-small
- **Graph Database**: Neo4j
- **Vector Database**: ChromaDB
- **Relational DB**: PostgreSQL
- **Document Parsing**: PyPDF2, python-docx, markdown
- **Language**: Python 3.12

## 📈 Roadmap

- [x] Phase 0: Project Setup
- [x] Phase 1: Document Ingestion
- [x] Phase 2: Entity Extraction
- [x] Phase 3: Relationship Mapping
- [x] Phase 4: Semantic Search
- [x] Phase 5: Multi-Hop Reasoning
- [ ] Phase 6: Insights & Timeline Generation
- [ ] Phase 7: Graph Visualization
- [ ] Phase 8: Export to HTML/PDF

## 🐛 Troubleshooting

### Docker containers not starting
```bash
docker-compose down
docker-compose up -d
docker ps  # Verify all containers are running
```

### Neo4j connection refused
```bash
docker start mindweave-neo4j
# Wait 30 seconds for Neo4j to fully start
```

### OpenAI API errors
- Verify API key in `.env`
- Check your OpenAI account has credits
- Ensure you're not hitting rate limits

### Module import errors
```bash
# Make sure you're in the project root
cd /path/to/mindweave
streamlit run AI/ui/streamlit_app.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Graph database by [Neo4j](https://neo4j.com/)
- Vector search by [ChromaDB](https://www.trychroma.com/)

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/mindweave](https://github.com/yourusername/mindweave)

---

⭐ **Star this repo if you find it useful!**

Made with ❤️ and 🤖 AI
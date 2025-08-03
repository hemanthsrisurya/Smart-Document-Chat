# 🚀 Smart Document Chat

*Transform your PDFs into intelligent conversations with AI*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Gemma3:4B-green.svg)](https://ollama.ai)
[![Windows](https://img.shields.io/badge/Windows-10/11-blue.svg)](https://microsoft.com)

## 🎯 What is this?

A lightning-fast, AI-powered document assistant that turns any PDF into an interactive chatbot. Upload your documents, ask questions in natural language, and get accurate answers with source citations - all running locally on your Windows machine.

**Perfect for:** Researchers, students, professionals, or anyone who needs to quickly extract insights from documents.

## ✨ Key Features

- **🧠 Smart AI Responses** - Powered by Gemma3:4B LLM for accurate, contextual answers
- **📚 Multi-Document Support** - Upload and query across multiple PDFs simultaneously  
- **💾 Persistent Storage** - Documents stay loaded between sessions - no re-uploading needed
- **🔍 Source Citations** - Every answer includes references to specific document sections
- **🎨 Beautiful Interface** - Clean, intuitive Streamlit web interface
- **🔒 Privacy First** - Everything runs locally - your documents never leave your system
- **🪟 Windows Optimized** - Specifically designed and tested for Windows 10/11

## 🚀 Quick Start

### Option 1: One-Click Installation (Recommended)
1. Download the project files
2. Right-click on `install.ps1` → "Run with PowerShell"
3. Wait for automatic setup (10-15 minutes)
4. App launches automatically in your browser!

### Option 2: Simple Double-Click
1. Download the project files
2. Double-click `start_app.bat`
3. Follow any setup prompts
4. Visit http://localhost:8501

### Option 3: Docker
```bash
docker-compose up -d
```
Then visit: http://localhost:8501

### Option 4: Manual Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Install Ollama from https://ollama.ai
ollama serve
ollama pull gemma3:4b

# Start the application
streamlit run app.py
```

## 📖 How to Use

### First Time Setup
1. **Upload PDFs** - Use the sidebar file uploader or drag & drop
2. **Process Documents** - Click "🚀 Process These PDFs" 
3. **Start Chatting** - Ask questions about your documents!

### Example Questions
- "Summarize the main findings in this research"
- "What are the key recommendations?"
- "Find all mentions of [specific topic]"
- "Compare different approaches discussed"

## 🏗️ Project Structure

```
smart-document-chat/
├── 📱 Core Application
│   ├── app.py                   # Streamlit web interface
│   ├── chatbot.py              # Main orchestrator
│   ├── config.py               # Configuration system
│   └── requirements.txt        # Dependencies
├── 🔧 Processing Modules  
│   ├── document_processor.py   # PDF processing
│   ├── vector_store.py         # ChromaDB management
│   ├── llm_handler.py          # Gemma3:4B integration
│   └── utils.py                # Helper utilities
├── 📁 Data Directories
│   ├── pdfFiles/               # PDF storage
│   ├── vectorDB/               # Vector embeddings
│   └── logs/                   # Application logs
├── 🐳 Docker
│   ├── Dockerfile
│   └── docker-compose.yml
└── 🚀 Windows Tools
    ├── install.ps1             # Auto-installer
    ├── run_app.ps1             # Advanced launcher
    ├── start_app.bat           # Simple launcher
    └── validate_setup.py       # Health checker
```

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **AI Model**: Gemma3:4B via Ollama
- **Vector Database**: ChromaDB for semantic search
- **Document Processing**: PyPDF for text extraction
- **Framework**: LangChain for RAG pipeline

### Core Components
1. **Document Processor** - Handles PDF upload, text extraction, and chunking
2. **Vector Store Manager** - Manages ChromaDB embeddings and similarity search
3. **LLM Handler** - Interfaces with Gemma3:4B for response generation
4. **RAG Chatbot** - Orchestrates the entire pipeline
5. **Streamlit App** - Provides the web interface

### Data Flow
```
PDF Upload → Text Extraction → Chunking → Embeddings → Vector Store
     ↓
User Question → Similarity Search → Context Retrieval → LLM → Response
```

## 🛠️ Troubleshooting

### Common Issues

**❌ "Python not found"**
- Install Python 3.8+ from https://python.org
- Check "Add to PATH" during installation

**❌ "Ollama not responding"**
- Install Ollama from https://ollama.ai
- Run: `ollama serve`
- Run: `ollama pull gemma3:4b`

**❌ "Port 8501 in use"**
- Close other Streamlit apps
- Use different port: `streamlit run app.py --server.port 8502`

**❌ "Module not found"**
- Run: `pip install -r requirements.txt`
- Ensure you're in the project directory

### Development Setup
```powershell
# Clone and setup
git clone <your-repo>
cd smart-document-chat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run with debugging
streamlit run app.py --logger.level debug
```

## 📄 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- **Ollama** for local LLM hosting
- **ChromaDB** for vector database capabilities  
- **LangChain** for RAG framework
- **Streamlit** for the beautiful web interface
- **Gemma3:4B** model by Google for intelligent responses


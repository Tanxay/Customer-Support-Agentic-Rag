# 🤖 Agentic RAG Customer Support System (MCP Enhanced)

A high-performance, privacy-focused **Agentic RAG (Retrieval-Augmented Generation)** system designed for intelligent customer support. This project utilizes a multi-agent architecture orchestrated by **LangGraph** to process complex user queries, routing them efficiently between vector search (PDFs), structured data lookups (SQL/MCP), and general conversation.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User[User] -->|Interacts| UI[Streamlit Frontend]
    UI -->|HTTP POST /query| API[FastAPI Backend]
    
    subgraph "LangGraph Workflow"
        API -->|Invoke| Router[Router Agent]
        
        Router -->|Intent: Policy/Docs| Retriever[Retrieval Agent]
        Router -->|Intent: Structured Data| SQL[SQL Agent (MCP)]
        Router -->|Intent: General| Answer[Answer Agent]
        
        Retriever -->|Hybrid Search| Milvus[(Milvus DB)]
        Retriever -->|Keyword Search| BM25[(BM25 Index)]
        
        SQL -->|SQL Query| SQLite[(SQLite DB)]
        
        Milvus -->|Top-K Docs| Answer
        BM25 -->|Chunks| Answer
        SQLite -->|Exact Data| Answer
    end
    
    Answer -->|Context + Query| LLM["Ollama (Llama 3.2)"]
    LLM -->|Generated Response| UI
```

![System Architecture](system_architecture.png)

## 🚀 Key Features

### 1. **Data-Aware Routing (Agentic Workflow)**
The **Router Agent** intelligently classifies user intent:
*   **Vector Search**: For unstructured text (PDFs, Manuals, Text files).
*   **Direct SQL (MCP)**: For structured data questions (e.g., "How many orders are pending?").
*   **General Chat**: For greetings and identity commands.

### 2. **Model Context Protocol (MCP) / SQL Agent**
Unlike standard RAG which "guesses" at numbers, our **SQL Agent** turns natural language into real SQL queries.
*   *User*: "What is the average price of pending orders?"
*   *Agent*: `SELECT AVG(price) FROM orders WHERE status='Pending';`
*   *Result*: 100% accurate mathematical answers.

### 3. **Hybrid Search (BM25 + Milvus)**
Combines semantic understanding (dense vectors) with exact keyword matching (sparse vectors) to ensure technical error codes (e.g., "E-505") are never missed.

### 4. **Streaming UI (Typewriter Effect)**
The Streamlit frontend simulates a real-time typing effect, providing a responsive and engaging user experience.

### 5. **Multi-File Support**
Ingests a wide variety of formats:
*   `PDF`, `TXT`, `DOCX`, `PPTX` (Vectorized)
*   `XLSX`, `CSV` (Converted to SQL Database)

---

## 🛠️ Project Structure

```text
app/
├── agents/       # The "Brain": Router, Retrieval, Answer, and SQL agents
├── workflow/     # The "Skeleton": LangGraph orchestration logic
├── api/          # The "Mouth": FastAPI backend server
├── frontend/     # The "Face": Streamlit user interface
├── ingestion/    # The "Stomach": Data processing (Vector + SQL conversion)
└── core/         # Configuration & Constants
```

---

## ⚡ Setup & Installation

### Prerequisites
1.  **Docker Desktop** (for Milvus).
2.  **Ollama** (Install from [ollama.com](https://ollama.com)).
3.  **Python 3.10+**.

### Step 1: Install Models
```powershell
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

### Step 2: Start Database
```powershell
docker-compose up -d
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
# Ensure you have the new SQL dependencies:
pip install sqlalchemy langchain-experimental
```

### Step 4: Ingest Data
Place your files in the `data/` folder and run:
```powershell
# 1. Ingest Text/PDFs into Milvus
python -m app.ingestion.ingest

# 2. Convert Excel to SQL Database
python -m app.ingestion.convert_db
```

### Step 5: Run the App
**Terminal 1 (Backend):**
```powershell
python -m app.api.server
```

**Terminal 2 (Frontend):**
```powershell
streamlit run app/frontend/app.py
```

---

## 🧪 Usage Examples

**1. Text Search (Manuals)**
> "How do I reset the Wi-Fi?"
> "What does the purple light mean?"

**2. Structured Data (SQL/MCP)**
> "How many orders are in the database?"
> "List all orders with status 'Shipped'."
> "What is the total value of all orders?"

# System Design & Architecture Document

## 1. Agentic Workflow Design
The system utilizes a **Multi-Agent Architecture** orchestrated by **LangGraph**. Unlike traditional linear chains (RAG-chains), this design implements a stateful, cyclic workflow that allows for dynamic decision-making.

### **Core Components:**
*   **Router Agent (The "Dispatcher"):**
    *   **Role**: Analyzes the user's intent classification (Zero-shot classification).
    *   **Logic**:
        *   If intent is `policy_query` or `data_lookup` $\rightarrow$ Route to **Retrieval Agent**.
        *   If intent is `general_chat` $\rightarrow$ Route to **Answer Agent** (Direct LLM).
*   **Retrieval Agent (The "Researcher"):**
    *   **Role**: Fetches relevant context from the knowledge base.
    *   **Logic**: Executes **Hybrid Search** (Vector + Keyword) and passes the top-k document chunks to the Answer Agent.
*   **Answer Agent (The "Writer"):**
    *   **Role**: Synthesizes the final response.
    *   **Logic**: Combines the original query + retrieved context (if any) to generate a grounded, hallucination-free response.

**Diagrammatic Flow:**
`Start` $\rightarrow$ `Router` $\rightarrow$ (`Retrieval` $\rightarrow$ `Answer`) OR (`Answer`) $\rightarrow$ `End`

---

## 2. Context Construction Strategy
To maximize retrieval accuracy and minimize hallucinations, we employ a **Hybrid Retrieval Strategy**:

*   **Dual-Index Approach**:
    1.  **Dense Index (Semantic Search)**: Uses **Milvus** with `nomic-embed-text` embeddings. Captures the *meaning* of the query (e.g., "broken device" matches "defective hardware").
    2.  **Sparse Index (Keyword Search)**: Uses **BM25** (Best Matching 25). Captures *exact matches* (e.g., "Error Code 505" or specific Product IDs).
*   **Fusion Logic**:
    *   We utilize **Reciprocal Rank Fusion (RRF)** via `EnsembleRetriever` to combine results from both indices.
    *   **Weights**: 50% Vector / 50% Keyword.
*   **Prompt Engineering**:
    *   Retrieved chunks are formatted as: `Source: [filename] \n Content: [text extraction]`.
    *   The System Prompt explicitly enforces citation ("Always cite the source") and prohibits using outside knowledge for factual queries.

---

## 3. Technology Choices & Rationale

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Orchestration** | **LangGraph** | Enables cyclic workflows (looping) and state management, which are impossible with standard LangChain linear chains. Crucial for future expansion (e.g., "Re-write search query if no results found"). |
| **LLM Inference** | **Ollama** | **Privacy & Cost**. Runs 100% locally. No data leaves the premise. Zero API costs. |
| **Vector DB** | **Milvus** | **Scale**. Unlike file-based DBs (Chroma/FAISS), Milvus is a production-grade, distributed vector database running in Docker, capable of handling millions of vectors without latency degradation. |
| **Backend API** | **FastAPI** | **Performance**. Asynchronous Python framework standard for AI agents. Provides automatic Swagger documentation and Type safety (Pydantic). |
| **Frontend** | **Streamlit** | **Rapid Dev**. chosen for its ability to visualize data and chat interfaces purely in Python, allowing us to focus on agent logic rather than JavaScript. |

---

## 4. Key Design Decisions

1.  **Decoupled Frontend/Backend**:
    *   We separated the UI (Streamlit) from the Logic (FastAPI).
    *   **Why?**: Allows other interfaces (e.g., a Mobile App, Slack Bot, or Whatsapp integration) to plug into the same Intelligence API without code changes.

2.  **Local-First Architecture**:
    *   Designed to run entirely offline (Air-gapped capable).
    *   **Why?**: Critical for enterprise Customer Support where data privacy (PII) is paramount.

3.  **Strict File Validation**:
    *   Ingestion pipeline strictly validates MIME types (`pdf`, `csv`, `docx`, etc.) and sanitizes metadata.
    *   **Why?**: Prevents database corruption and ensures the schema in Milvus remains consistent (Alignment errors).

---

## 5. Limitations

1.  **Hardware Dependency (Latency)**:
    *   Running an LLM (Llama 3.2), Vector DB (Milvus), and API on a single machine with limited RAM (e.g., 4GB) causes Operating System memory swapping. This results in high latency (60s+ responses) purely due to hardware constraints, not software inefficiency.

2.  **Context Window**:
    *   While Llama 3.2 supports decent context, local hardware limits how much text we can shove into the "Context Window" before memory overflows. We limit retrieval to Top-5 chunks to remain safe.

3.  **No Persistence**:
    *   Chat history is currently in-memory (Session State). Reloading the browser clears the conversation history. A production upgrade would require a PostgreSQL database to store chat logs.

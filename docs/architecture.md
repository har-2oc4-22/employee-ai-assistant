# Architecture — Employee AI Assistant

## System Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["🖥️ React Frontend (Vite + Tailwind)"]
        UI["Chat UI (App.jsx)"]
        Hook["useChat Hook"]
        API_SVC["api.js (Axios)"]
    end

    subgraph Backend["⚙️ FastAPI Backend (Python 3.11+)"]
        ROUTES["API Routes\n/chat  /health  /ingest\n/employees  /conversations"]
        CHAT_SVC["Chat Service"]
        AGENT["LangChain Agent\n(Tool-Calling Loop)"]
        
        subgraph Tools["🛠️ Agent Tools"]
            T1["search_company_documents"]
            T2["get_employee_info"]
            T3["apply_leave"]
        end
        
        subgraph RAG["📚 RAG Pipeline"]
            INGEST["Ingestion Pipeline\n(Loader → Splitter → Embed)"]
            RETRIEVER["Retriever\n(Threshold Filter)"]
            VS["Vector Store\n(ChromaDB Abstraction)"]
        end
        
        subgraph Memory["🧠 Conversation Memory"]
            STATE["In-Memory Store\n(conversation_id → messages)"]
        end
        
        EMP_SVC["Employee Service\n(JSON persistence)"]
        PROMPTS["Prompts\n(agent_prompts.py\nrag_prompts.py)"]
    end

    subgraph External["☁️ External Services"]
        GEMINI["Google Gemini API\n(Chat + Embeddings)"]
        CHROMA["ChromaDB\n(Persistent on Disk)"]
        DOCS["Company Documents\n(MD / PDF / TXT)"]
        EMP_DB["employees.json"]
        LEAVE_DB["leave_requests.json"]
    end

    %% Frontend connections
    UI --> Hook
    Hook --> API_SVC
    API_SVC -->|"POST /chat"| ROUTES

    %% Backend flow
    ROUTES --> CHAT_SVC
    CHAT_SVC --> AGENT
    AGENT --> Tools
    AGENT --> STATE
    AGENT --> GEMINI
    
    %% Tool connections
    T1 --> RETRIEVER
    T2 --> EMP_SVC
    T3 --> EMP_SVC
    
    %% RAG connections
    RETRIEVER --> VS
    VS --> CHROMA
    INGEST --> VS
    DOCS --> INGEST
    INGEST --> GEMINI
    
    %% Data connections
    EMP_SVC --> EMP_DB
    EMP_SVC --> LEAVE_DB
    
    %% Prompts
    PROMPTS --> AGENT
```

---

## RAG Pipeline Detail

```mermaid
flowchart TD
    A["📁 Company Documents\n(leave_policy.md, wfh_policy.md, etc.)"] 
    --> B["📄 Document Loader\n(PyPDFLoader / TextLoader)"]
    --> C["✂️ Text Chunker\n(RecursiveCharacterTextSplitter\nchunk_size=800, overlap=150)"]
    --> D["🔢 Gemini Embeddings\n(models/gemini-embedding-001)"]
    --> E["💾 ChromaDB\n(Persistent Vector Store)"]

    F["👤 User Query"] 
    --> G["🔢 Query Embedding\n(same model)"]
    --> H["🔍 Similarity Search\n(top-k=4)"]
    --> E
    E --> H
    H --> I{"Relevance Score\n≥ threshold?"}
    I -->|"Yes"| J["📋 Retrieved Chunks\n(with source metadata)"]
    I -->|"No"| K["⚠️ No Answer\n(Hallucination Prevented)"]
    J --> L["📝 Prompt Construction\n(context + question)"]
    L --> M["🤖 Google Gemini 3.6 Flash\n(generates answer from context only)"]
    M --> N["✅ Answer + Sources"]
```

---

## Agent Tool-Calling Flow

```mermaid
sequenceDiagram
    participant User
    participant React
    participant FastAPI
    participant Agent
    participant Gemini
    participant ChromaDB
    participant EmployeeDB

    User->>React: "What is the leave policy and how many leaves do I have?"
    React->>FastAPI: POST /chat {employee_id, message, conversation_id}
    FastAPI->>Agent: run_agent(employee_id, message, history)
    
    Agent->>Gemini: [System Prompt + History + User Message]
    Gemini-->>Agent: tool_calls: [search_company_documents, get_employee_info]
    
    Agent->>ChromaDB: similarity_search("leave policy")
    ChromaDB-->>Agent: [relevant chunks + metadata]
    
    Agent->>EmployeeDB: get_employee("EMP001")
    EmployeeDB-->>Agent: {name, department, leave_balance: 12}
    
    Agent->>Gemini: [Tool Results + Combine]
    Gemini-->>Agent: "According to the leave policy... You have 12 days remaining."
    
    Agent-->>FastAPI: {answer, sources, tools_used, conversation_id}
    FastAPI-->>React: JSON response
    React-->>User: Renders answer with sources and tool badges
```
![alt text](mermaid-diagram.png)
---

## Data Flow Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Vite + Tailwind | Chat UI |
| HTTP | Axios | Frontend → Backend |
| API | FastAPI + Uvicorn | REST endpoints |
| Agent | LangChain tool-calling | Multi-step reasoning |
| LLM | Google Gemini 3.6 Flash | Language understanding & generation |
| Embeddings | Google Gemini models/gemini-embedding-001 | Semantic search |
| Vector DB | ChromaDB (persistent) | Document chunk storage & search |
| Documents | MD / PDF / TXT files | Company knowledge base |
| Employee DB | JSON file | Mock employee database |
| Memory | In-memory dict | Conversation history |

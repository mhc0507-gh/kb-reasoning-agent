# Reasoning Diagnostic Agent

An AI-powered diagnostic agent system that performs automated root cause analysis for system alerts and issues. The system uses multiple AI agents orchestrated through LangGraph, with access to system monitoring tools and a knowledge base of diagnostic procedures.

## Overview

This project implements a multi-agent diagnostic system that:
- Analyzes system alerts and identifies root causes
- Uses Retrieval-Augmented Generation (RAG) to access diagnostic knowledge base
- Queries system metrics through MCP (Model Context Protocol) servers
- Orchestrates diagnostic workflows using LangGraph
- Supports agent-to-agent communication via A2A protocol

## Architecture

The system consists of several key components:

### MCP Servers

**MCP HTTP Server** (`MCP_http_server.py`): Provides HTTP-based access to system monitoring tools
- System load queries
- System latency monitoring
- Link status checks
- Service and deployment information
- CPU load and request rate metrics

**MCP Local Server** (`MCP_local_server.py`): Provides local STDIO-based access to diagnostic knowledge base
- RAG-powered failure analysis knowledge base
- Diagnostic procedure retrieval

### Core Agents

**Diagnostic Agent** (`diagnostic_agent.py`): Main orchestrator that:
- Connects to both MCP servers (HTTP and STDIO)
- Uses LangGraph's ReAct agent pattern
- Queries knowledge base to create diagnostic plans
- Executes diagnostic procedures using available tools
- Performs iterative root cause analysis

**Response Agent** (`response_agent.py`): Evaluates diagnostic agent outputs against reference responses for testing and benchmarking. It provides two evaluation modes:
- **LLM-based similarity** (`compare_agent_LLM`): Uses a structured prompt so an LLM checks whether every key detail from a reference response is present in the generated response. Returns a JSON with a 0–100 score, a list of missing or partially present details, and a short explanation.
- **Sentence-Transformer similarity** (`compare_agent_ST`): Computes cosine similarity between the response and reference using the `all-MiniLM-L6-v2` embedding model and returns a 0–100 integer score. Useful for fast, embedding-based similarity checks.

**A2A Diagnostic Agent** (`a2a_diagnostic_agent.py`): Exposes the diagnostic agent as an A2A-compatible service
- Runs on port 9001
- Accepts diagnostic queries via A2A protocol
- Returns formatted diagnostic results

**A2A Client** (`a2a_client.py`): Client implementation for agent-to-agent communication
- Can invoke other A2A agents
- Used in multi-agent workflows

### Knowledge Base

**Diagnostic KB** (`diagnostic_kb.py`): RAG system implementation
- Uses ChromaDB for vector storage
- Sentence transformers for embeddings
- Retrieves relevant diagnostic procedures based on queries

**Diagnostic Docs** (`diagnostic_docs.py`): Sample diagnostic procedures and knowledge base content

### Utilities

**Tool Trace** (`tool_trace.py`): Logging and debugging utilities for agent execution traces

### Colab Notebook

**Diagnostic Agent Notebook** (`Colab_Notebooks/diagnostic_agent.ipynb`): A self-contained Jupyter/Colab notebook that runs the full diagnostic pipeline in a single environment (tested on Python 3.12.7). It uses cloud LLMs instead of Ollama:
- **Setup**: Loads API keys from `.env` (e.g. `GOOGLE_API_KEY`, `GROQ_API_KEY`), generates and installs a notebook-specific `requirements.txt` (Chromadb, FastMCP, LangChain, LangGraph, LangChain Google GenAI, LangChain Groq, etc.).
- **Knowledge base**: Defines the same sample diagnostic documents (connection/latency/CPU procedures) and implements a `DiagnosticKB` class with RAG (ChromaDB + sentence-transformers `all-MiniLM-L6-v2`).
- **MCP HTTP server**: Defines and starts the same MCP tools in-process (failure analysis KB, system load/latency, link status, high-latency percentage, request latencies, service/deployment info, CPU load, requests/sec) via FastMCP streamable-HTTP on `localhost:8000/mcp`, with optional cells to check or stop the server.
- **Diagnostic agent**: MCP client that loads tools, builds a ReAct agent with `create_react_agent`, and supports **Gemini** (`gemini-2.5-flash`) or **Groq** (`llama-3.3-70b-versatile`) via `get_llm()`. Includes the same “query KB first, then execute plan” prompt.
- **Run**: Executes the agent on the example query for origin service high-latency alert and prints the response.

Use this notebook to try the diagnostic agent in Google Colab or any Jupyter environment without running Ollama or separate MCP servers.

## Prerequisites

- Python 3.13
- Ollama installed and running with compatible models:
  - `gpt-oss:20b` (for diagnostic agent)
  - `llama3.2` (for response agent)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Reasoning-Diagnostic-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running and has the required models:
```bash
ollama pull gpt-oss:20b
ollama pull llama3.2
```

## Usage

### Running the MCP HTTP Server

Start the HTTP-based MCP server:
```bash
python MCP_http_server.py
```

The server will run on `http://localhost:8000/mcp`

### Running the A2A Diagnostic Agent Server

Start the A2A-compatible diagnostic agent service:
```bash
python a2a_diagnostic_agent.py
```

The server will run on `http://localhost:9001/`

### Running the Diagnostic Agent Directly

Run the diagnostic agent with a query:
```bash
python diagnostic_agent.py
```

For verbose logging:
```bash
python diagnostic_agent.py -verbose
```

### Running the Multi-Agent Workflow

Run the complete diagnostic workflow with response formatting:
```bash
python a2a_client.py
```

### Running the Colab / Jupyter Notebook

Open `Colab_Notebooks/diagnostic_agent.ipynb` in Google Colab or Jupyter. Set `GOOGLE_API_KEY` and/or `GROQ_API_KEY` in your environment or a `.env` file, then run all cells. The notebook starts the MCP server in-process and runs the diagnostic agent with Gemini or Groq on the example high-latency alert query.

## Example Queries

The system can handle queries like:
- "What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'"
- Connection failure diagnostics
- High latency diagnostics
- CPU usage diagnostics

## How It Works

1. **Query Reception**: User submits a diagnostic query
2. **Knowledge Base Query**: Agent queries the RAG knowledge base to retrieve relevant diagnostic procedures
3. **Plan Creation**: Agent creates a diagnostic plan based on retrieved procedures
4. **Tool Execution**: Agent executes tools from MCP servers to gather system metrics
5. **Iterative Analysis**: Agent iteratively refines analysis based on tool results
6. **Root Cause Determination**: Agent continues until root cause is identified or determined to be unknown
7. **Evaluation (optional)**: Response agent can compare the diagnostic result to a reference response for benchmarking (LLM or embedding-based similarity scoring)

## Sample Test Results

Benchmark runs are recorded in **`RESULTS.md`**. Each run executes the diagnostic agent multiple times on the same high-latency alert query and evaluates outputs with the response agent's **LLM similarity** and **Sentence-Transformer (ST) similarity** scores (0–100). Reported metrics:

- **Diagnostic_elapsed_time (s)**: Time per diagnostic run.
- **LLM_similarity_score**: Score from the LLM evaluator (key-detail coverage vs reference).
- **ST_similarity_score**: Cosine-similarity score from embeddings (`all-MiniLM-L6-v2`).

Summary from sample runs (20 iterations per model):

| Model | Diagnostic time (mean ± std) | LLM similarity (mean ± std) | ST similarity (mean ± std) | Total time |
|-------|------------------------------|-----------------------------|----------------------------|------------|
| **gpt-oss:20b** | 167.10 s ± 16.12 | 76.00 ± 17.90 | 55.35 ± 4.89 | 88.3 min |
| **granite4:32b-a9b-h** | 218.10 s ± 20.16 | 31.00 ± 16.45 | 54.15 ± 3.47 | 99.4 min |

See [`RESULTS.md`](RESULTS.md) for per-iteration tables and full details.

## Project Structure

```
Reasoning-Diagnostic-Agent/
├── Colab_Notebooks/
│   └── diagnostic_agent.ipynb   # Self-contained Colab/Jupyter notebook (cloud LLMs, in-process MCP + agent)
├── MCP_http_server.py          # HTTP-based MCP server with system tools
├── MCP_local_server.py          # Local STDIO-based MCP server with KB
├── diagnostic_agent.py          # Main diagnostic agent orchestrator
├── a2a_diagnostic_agent.py      # A2A server wrapper for diagnostic agent
├── a2a_client.py                # A2A client and multi-agent workflow
├── response_agent.py            # Evaluation of diagnostic outputs vs reference (LLM + embedding similarity)
├── diagnostic_kb.py             # RAG knowledge base implementation
├── diagnostic_docs.py           # Diagnostic procedure documents
├── tool_trace.py                # Logging and debugging utilities
├── RESULTS.md                   # Sample benchmark results (diagnostic time, LLM/ST similarity by model)
└── requirements.txt             # Python dependencies
```

## Dependencies

- `a2a-sdk`: Agent-to-agent communication protocol
- `chromadb`: Vector database for RAG
- `fastmcp`: Fast MCP server implementation
- `langchain`: LLM framework
- `langchain_ollama`: Ollama integration for LangChain
- `langchain-mcp-adapters`: MCP adapters for LangChain
- `langgraph`: Agent orchestration framework
- `mcp`: Model Context Protocol SDK
- `sentence-transformers`: Embedding models for RAG

## Configuration

### Model Configuration

Edit the model names in:
- `diagnostic_agent.py`: Change `model = "gpt-oss:20b"` to your preferred diagnostic model
- `response_agent.py`: Change `model = "llama3.2"` to your preferred response formatting model

### Server Configuration

- MCP HTTP Server: Configure host, port, and path in `MCP_http_server.py`
- A2A Server: Configure host and port in `a2a_diagnostic_agent.py`
- A2A Client: Update agent URLs in `a2a_client.py` if needed

## Logging

The system supports multiple log levels:
- `NORMAL`: Standard output
- `VERBOSE`: Detailed tool execution traces
- `TRACE`: Additional debugging information
- `DEBUG`: Full debugging output

Use the `-verbose` flag when running `diagnostic_agent.py` for detailed execution traces.

## Extending the System

### Adding New Diagnostic Procedures

Add new diagnostic procedures to `diagnostic_docs.py`. The RAG system will automatically index them.

### Adding New Tools

Add new tools to `MCP_http_server.py` using the `@mcp_http_server.tool()` decorator.

### Customizing the Knowledge Base

Modify `diagnostic_kb.py` to:
- Change the embedding model
- Adjust retrieval parameters
- Add custom document processing

## License

This repository is licensed under the [MIT license](../LICENSE).


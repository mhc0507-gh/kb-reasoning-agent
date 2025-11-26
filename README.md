# Reasoning Diagnostic Agent

Technology demonstration PoC of an **AI agent** using **LLM**-based **reasoning** to perform complex tasks: generate an execution plan from external inputs and a knowledge base, collect relevant external data via integrated tools, evaluate if the goal has been achieved, and deliver actionable conclusions—powered by **Ollama** with **open-source models**.

## Overview

This project demonstrates advanced AI agent capabilities through a multi-agent system that combines:

- **LLM-based reasoning** for complex problem-solving and decision-making
- **ReAct agent** pattern for iterative reasoning and action execution
- **RAG** (Retrieval-Augmented Generation) for knowledge base integration
- **LangChain** and **LangGraph** for agent orchestration and workflow management
- **MCP** (Model Context Protocol) for tool integration and external data access
- **A2A** (Agent-to-Agent) protocol for multi-agent communication and coordination
- **Ollama** integration for running open-source LLM models locally

## Technology Stack

- **LangChain**: LLM application framework for building LLM-powered applications
- **LangGraph**: State machine framework for orchestrating agent workflows and state management
- **Ollama**: Local LLM runtime for open-source model execution
- **ReAct Agent**: Reasoning and Acting pattern combining thought and action for iterative reasoning loops
- **RAG**: Retrieval-Augmented Generation for knowledge-enhanced responses and knowledge base integration
- **MCP**: Model Context Protocol SDK for standardized tool and data integration
- **A2A SDK**: Agent-to-Agent communication protocol for distributed agent systems
- **ChromaDB**: Vector database for RAG semantic search
- **Sentence Transformers**: Embedding models for semantic search
- **Open-source Models**: Community-driven LLM models (e.g., GPT-OSS, Llama)

## Architecture

The system demonstrates how to build an AI agent that:

1. **Receives external inputs** (queries, alerts, tasks)
2. **Queries a knowledge base** using RAG to retrieve relevant procedures and information
3. **Generates execution plans** based on retrieved knowledge and current context
4. **Collects external data** via integrated tools through MCP servers
5. **Evaluates progress** and iteratively refines the approach
6. **Delivers actionable conclusions** with supporting evidence

### Core Components

- **Agent Orchestration**: LangGraph-based state machines for workflow management
- **Knowledge Base**: RAG system with vector embeddings for semantic search
- **Tool Integration**: MCP servers providing standardized access to external tools and data
- **Multi-Agent Communication**: A2A protocol for agent-to-agent interactions
- **LLM Backend**: Ollama-powered inference with open-source models

## Demo Use Case: Diagnostic Agent

This PoC implements a diagnostic agent system that performs automated root cause analysis, demonstrating the core capabilities:

- Analyzes system alerts and identifies root causes
- Uses RAG to access diagnostic knowledge bases
- Queries system metrics through MCP servers
- Orchestrates diagnostic workflows using LangGraph
- Supports agent-to-agent communication via A2A protocol

See the `Reasoning-Diagnostic-Agent/` subdirectory for the complete implementation.

## System Requirements

### Hardware Requirements

The PoC has been tested and runs completely local on the following hardware configuration:

- **Operating System**: Windows 11
- **Processor**: Intel(R) Core(TM) Ultra 7 265 (2.40 GHz) or equivalent
- **Memory**: 32.0 GB RAM
- **GPU**: Not required (runs on CPU only)

**Note**: The system runs entirely locally without GPU acceleration. While the above configuration has been verified, the minimum requirements may vary depending on the specific LLM models used and workload complexity.

### Software Requirements

- **Python**: 3.13
- **Ollama**: Installed and running with compatible open-source models
- **Operating System**: Windows 11 (tested), or compatible Windows/Linux/macOS system

## Getting Started

1. Navigate to the project directory:
```bash
cd Reasoning-Diagnostic-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Ollama with required models:
```bash
ollama pull gpt-oss:20b
ollama pull llama3.2
```

4. Run the system:
```bash
python a2a_diagnostic_agent.py
```

## Project Structure

```
Repo/
├── Reasoning-Diagnostic-Agent/    # Main project implementation
│   ├── diagnostic_agent.py        # Core agent with ReAct pattern
│   ├── a2a_diagnostic_agent.py     # A2A server wrapper
│   ├── MCP_http_server.py          # MCP server with tools
│   ├── diagnostic_kb.py            # RAG knowledge base
│   └── ...
└── README.md                       # This file
```

## Key Features Demonstrated

- ✅ LLM-based reasoning and planning
- ✅ RAG for knowledge retrieval
- ✅ ReAct agent pattern implementation
- ✅ LangGraph workflow orchestration
- ✅ MCP tool integration
- ✅ A2A multi-agent communication
- ✅ Ollama with open-source models
- ✅ Iterative problem-solving loops
- ✅ External data collection and evaluation

## License

This repository is licensed under the [MIT license](LICENSE).

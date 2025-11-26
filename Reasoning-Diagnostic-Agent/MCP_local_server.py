from fastmcp import FastMCP
from diagnostic_kb import DiagnosticKB

mcp_local_server = FastMCP("MCP-Local-Server")

# Initialize diagnostic knowledge base
diagnostic_kb = DiagnosticKB()

@mcp_local_server.tool()
def failure_analysis_kb(query: str):
    """Knowledge base for procedures on how to diagnose issues."""
    return diagnostic_kb.query_rag(query)

@mcp_local_server.prompt()
def get_llm_prompt(query: str) -> str:
    """Generates a prompt for the LLM to use to answer the query"""

    raise Exception("Not implemented")


if __name__ == "__main__":
    mcp_local_server.run(transport="stdio")
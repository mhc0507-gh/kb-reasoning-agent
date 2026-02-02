import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from tool_trace import ToolTrace

gpt_model = { "name": "gpt-oss:20b", "reasoning": True }
granite_model = { "name": "granite4:32b-a9b-h", "reasoning": False }

def get_llm(name: str|None) -> ChatOllama:
    match name:
        case "gpt-oss:20b":
            selected_model = gpt_model
        case "granite4:32b-a9b-h":
            selected_model = granite_model
        case _:
            selected_model = gpt_model

    return ChatOllama(
        model=selected_model["name"],
        reasoning=selected_model["reasoning"],
        disable_streaming=True,
        verbose=True
        )


def get_llm_prompt(query: str) -> str:
    return f"""
    You are a helpful assistant. Answer the following query
    by only using the tools provided to you. DO NOT make up any information.
    Query failure analysis KB first to make a plan on how to derive the
    response. Then execute the plan until root cause is determined for response.
    Do not repeat tool calls with the same query.

    If the result of a step in the plan indicates a new KB query is needed
    for root causing the issue then you MUST perform the new failure analysis KB query
    and make a new plan to derive the root cause response. DO NOT finish before
    the root cause is determined, unless the conclusion is "unable to determine
    root cause".

    Query: {query}
    """

async def query_agent(prompt: str, model: str|None=None, log_level=ToolTrace.NORMAL) -> str:
    # MCP server that runs locally communicating through STDIO
    mcp_local_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "MCP_local_server.py"))
    print(f"MCP local server path: {mcp_local_server_path}")

    server_params = StdioServerParameters(
        command="python",
        args=[mcp_local_server_path],
    )

    # MCP server accessible through HTTP
    mcp_http_server_url="http://localhost:8000/mcp"

    async with stdio_client(server_params) as (stdio_read, stdio_write):
        async with ClientSession(stdio_read, stdio_write) as stdio_session:
            print("initializing STDIO client session")
            await stdio_session.initialize()

            try:
                async with streamablehttp_client(mcp_http_server_url) as (http_read, http_write, _):
                    async with ClientSession(http_read, http_write) as http_session:
                        print("initializing HTTP client session")
                        await http_session.initialize()

                        print("\nloading tools & prompt")
                        # Tool names must be unique, the LLM will chose
                        # a tool based on the query and tool descriptions.
                        mcp_server_tools = await load_mcp_tools(http_session)
                        mcp_server_tools += await load_mcp_tools(stdio_session)

                        llm = get_llm(model)
                        llm_prompt = get_llm_prompt(prompt)

                        print("\nTools loaded :")
                        for tool in mcp_server_tools:
                            print(f"▪️ {tool.name} - {tool.description}")

                        config = None if log_level <= ToolTrace.NORMAL else RunnableConfig(callbacks=[ToolTrace(ToolTrace.VERBOSE)])

                        agent=create_react_agent(model=llm, tools=mcp_server_tools, debug=False)

                        print(f"\nAnswering query : {prompt}")
                        agent_response = await agent.ainvoke(input={"messages": llm_prompt}, config=config)

                        return agent_response["messages"][-1].content

            except Exception as e:
                print(f"Error: {e}")
                if isinstance(e, ExceptionGroup):
                    print(f"{e.exceptions}")
                return "Error"

    return "Error"

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    log_level = ToolTrace.NORMAL
    if args.verbose:
        log_level = ToolTrace.VERBOSE

    print("\nRunning Query Agent...")
    response = asyncio.run(
        query_agent(
            prompt="What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'",
            model=args.model,
            log_level=log_level)
        )

    print("\nResponse: ", response)
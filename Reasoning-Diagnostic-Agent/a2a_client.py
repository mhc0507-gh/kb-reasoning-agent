from typing import Any, TypedDict, Annotated
from uuid import uuid4

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage

import asyncio
import httpx
import json
import operator

import response_agent

from tool_trace import ToolTrace

async def execute_a2a_agent(agent_card_url: str,
                            user: str,
                            prompt: str | list[str | dict],
                            log_level=ToolTrace.NORMAL) -> str:

    print("Retrieving agent card at ", agent_card_url)
    async with httpx.AsyncClient(timeout=600) as httpx_client:

        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=agent_card_url,
        )

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            final_agent_card_to_use = _public_card

        except Exception as e:
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e

        client = A2AClient(httpx_client=httpx_client, agent_card=final_agent_card_to_use)
        print("A2AClient initialized.")

        input_dict = {"user": user, "prompt": prompt, "log_level": log_level}

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': json.dumps(input_dict)}
                ],
                'messageId': uuid4().hex,
            },
        }

        print("prompting agent")
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**send_message_payload)
        )
        response = await client.send_message(request)

        # Extract text from the response object
        response_json = response.model_dump(mode='json', exclude_none=True)
        text = response_json.get("result").get("parts")[0].get("text")
        print("Response from agent = ", text)
        return text


class DiagnosticAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class DiagnosticAgent:

    def __init__(self) -> None:

        diag_graph = StateGraph(DiagnosticAgentState)
        diag_graph.add_node("Diagnostic", self.diagnostic_agent_node)
        diag_graph.add_node("Response", self.response_agent_node)

        diag_graph.add_edge("Diagnostic", "Response")
        diag_graph.add_edge("Response", END)

        diag_graph.set_entry_point("Diagnostic")

        self.diag_graph = diag_graph.compile()

    def diagnostic_agent_node(self, state: DiagnosticAgentState):
        messages = state["messages"]

        # Call the diagnostic agent
        prompt = messages[0].content
        print(f"Diagnostic agent node received {prompt}")

        response = asyncio.run(execute_a2a_agent(
            agent_card_url="http://localhost:9001/",
            user="",
            prompt=prompt,
            log_level=ToolTrace.VERBOSE
        ))

        print(f"🤖 Diagnostic agent node response: {response}")

        return {"messages": [AIMessage(content=response)]}

    def response_agent_node(self, state: DiagnosticAgentState):
        messages = state["messages"]

        # Call LLM to format response
        ai_contents = [msg.text() for msg in messages if isinstance(msg, AIMessage)][0]
        print(f"Response agent node received {ai_contents}")

        response = asyncio.run(response_agent.query_agent(
            prompt=ai_contents
        ))

        print(f"🤖 Response agent node response: {response}")

        return {"messages": [AIMessage(content=response)]}


if __name__ == '__main__':

    diag_agent = DiagnosticAgent()

    diag_prompt = "What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'"
    user_message: DiagnosticAgentState = {"messages": [HumanMessage(diag_prompt)]}

    ai_response = diag_agent.diag_graph.invoke(user_message)

    print(f"\nAGENT: {ai_response["messages"][-1].content}")

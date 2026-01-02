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
import time

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
        return text


class DiagnosticAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class DiagnosticAgent:

    def __init__(self, reference_response: str) -> None:
        self.reference_response = reference_response

        diag_graph = StateGraph(DiagnosticAgentState)
        diag_graph.add_node("Diagnostic", self.diagnostic_agent_node)
        diag_graph.add_node("Response", self.response_agent_node)

        diag_graph.add_edge("Diagnostic", "Response")
        diag_graph.add_edge("Response", END)

        diag_graph.set_entry_point("Diagnostic")

        self.diag_graph = diag_graph.compile()

    def diagnostic_agent_node(self, state: DiagnosticAgentState) -> DiagnosticAgentState:
        messages = state["messages"]

        # Call the diagnostic agent
        prompt = messages[0].content

        start_time = time.time()
        response = asyncio.run(execute_a2a_agent(
            agent_card_url="http://localhost:9001/",
            user="",
            prompt=prompt,
            log_level=ToolTrace.VERBOSE
        ))
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time for execute_a2a_agent: {elapsed_time:.2f} seconds")

        return {"messages": [AIMessage(content=response)]}

    def response_agent_node(self, state: DiagnosticAgentState):
        messages = state["messages"]

        # Get similarity score between response and reference
        ai_contents = [msg.text() for msg in messages if isinstance(msg, AIMessage)][0]

        LLM_similarity_score = asyncio.run(response_agent.compare_agent_LLM(ai_contents, self.reference_response))
        print(f"🤖 Response agent node LLM similarity score: {LLM_similarity_score}")

        ST_similarity_score = asyncio.run(response_agent.compare_agent_ST(ai_contents, self.reference_response))
        print(f"🤖 Response agent node ST similarity score: {ST_similarity_score}")

        return {"messages": [AIMessage(content=LLM_similarity_score)]}


if __name__ == '__main__':

    reference_response = """
        The alert is triggered because the origin service is over-loaded with too many requests, which is causing CPU saturation and, in turn, high latency:

        * The origin service is running on a deployment where the average CPU load is 98% over the last hour.
        * This high CPU usage is due to the deployment receiving ≈500 requests/s while it has only 2 role instances, which results in ≈250 requests/s per instance—well above the 100 requests/s threshold.

        Because the CPU is saturated, the service cannot process requests quickly, leading to the observed high latency on more than 90% of requests.
    """

    diag_agent = DiagnosticAgent(reference_response)

    diag_prompt = "What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'"
    user_message: DiagnosticAgentState = {"messages": [HumanMessage(diag_prompt)]}

    ai_response = diag_agent.diag_graph.invoke(user_message)

    print(f"\nAGENT: {ai_response["messages"][-1].content}")

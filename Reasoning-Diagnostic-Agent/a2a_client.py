from typing import TypedDict, Annotated
from uuid import uuid4

from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
    TextPart
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
                            model: str | None = None,
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

        config = ClientConfig(httpx_client=httpx_client)
        client_factory = ClientFactory(config)
        client = client_factory.create(card=final_agent_card_to_use)

        print("A2AClient initialized.")

        input_dict = {"user": user, "prompt": prompt, "model": model, "log_level": log_level}

        message = Message(
            role=Role("user"),
            parts=[
                Part(TextPart(text=json.dumps(input_dict)))
            ],
            message_id=uuid4().hex,
        )

        print("prompting agent")
        # Streaming is enabled, iterate through response
        response = None
        async for chunk in client.send_message(message):
            response = chunk  # Keep the last chunk as the final response

        if response is None:
            raise RuntimeError("No response received from agent")

        # Extract text from the response Message object
        if not isinstance(response, Message):
            raise RuntimeError("Response is not a message")
        if not response.parts or len(response.parts) == 0:
            raise RuntimeError("Response message has no parts")

        # Get the first part and extract text from TextPart
        first_part = response.parts[0]
        if isinstance(first_part.root, TextPart):
            if hasattr(first_part.root, 'text') and first_part.root.text is not None:
                return first_part.root.text
            else:
                raise RuntimeError("Part does not have a text attribute")
        else:
            raise RuntimeError(f"Unexpected part type: {type(first_part)}")


class DiagnosticAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class DiagnosticAgent:

    def __init__(self, model: str, reference_response: str) -> None:
        self.model = model
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
            model=self.model,
            log_level=ToolTrace.VERBOSE
        ))
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time for execute_a2a_agent: {elapsed_time:.2f} seconds")

        return {"messages": [AIMessage(content=[{"Diagnostic_elapsed_time":elapsed_time}, response])]}

    def response_agent_node(self, state: DiagnosticAgentState):
        messages = state["messages"]

        # Get diagnostic elapsed time and AI contents
        diagnostic_elapsed_time = 0
        ai_contents = ""
        if messages and isinstance(messages[1], AIMessage):
            content = messages[1].content
            if isinstance(content, list):
                if len(content) > 0 and isinstance(content[0], dict):
                    diagnostic_elapsed_time = int(content[0].get("Diagnostic_elapsed_time", 0))
                if len(content) > 1 and isinstance(content[1], str):
                    ai_contents = content[1]

        # Get similarity score between response and reference
        LLM_similarity_result = asyncio.run(response_agent.compare_agent_LLM(ai_contents, self.reference_response))
        print(f"🤖 Response agent node LLM similarity result: {LLM_similarity_result}")

        # Ensure LLM_similarity_result ends with }
        LLM_similarity_result = LLM_similarity_result.strip()
        if not LLM_similarity_result.endswith('}'):
            LLM_similarity_result += '}'

        # Parse similarity score from JSON response
        LLM_similarity_score: int = 0
        try:
            data = json.loads(LLM_similarity_result)
            parsed_score = data.get("score")
            if not isinstance(parsed_score, int):
                print(f"Error: LLM score is not an integer")
            else:
                LLM_similarity_score = parsed_score
        except json.JSONDecodeError:
            print(f"Failed to parse LLM_similarity_result JSON")

        ST_similarity_score = asyncio.run(response_agent.compare_agent_ST(ai_contents, self.reference_response))
        print(f"🤖 Response agent node ST similarity score: {ST_similarity_score}")

        return {"messages": [AIMessage(content=[
            {"Diagnostic_elapsed_time":diagnostic_elapsed_time},
            {"LLM_similarity_score":LLM_similarity_score},
            {"ST_similarity_score":ST_similarity_score}])]}


if __name__ == '__main__':

    from stats import print_stats

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", default="1")
    parser.add_argument("--model", default=None)

    args = parser.parse_args()

    reference_response = """
        The alert is triggered because the origin service is over-loaded with too many requests, which is causing CPU saturation and, in turn, high latency:

        * The origin service is running on a deployment where the average CPU load is 98% over the last hour.
        * This high CPU usage is due to the deployment receiving ≈500 requests/s while it has only 2 role instances, which results in ≈250 requests/s per instance—well above the 100 requests/s threshold.

        Because the CPU is saturated, the service cannot process requests quickly, leading to the observed high latency on more than 90% of requests.
    """

    diag_agent = DiagnosticAgent(args.model, reference_response)

    diag_prompt = "What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'"
    user_message: DiagnosticAgentState = {"messages": [HumanMessage(diag_prompt)]}

    elapsed_time = []
    scores_llm = []
    scores_st = []

    iterations = int(args.iterations)
    for i in range(1, iterations+1):
        ai_response = diag_agent.diag_graph.invoke(user_message)

        print(f"\nAGENT #{i}: {ai_response["messages"][-1].content}")

        response_data = ai_response["messages"][-1].content
        elapsed_time.append(response_data[0].get("Diagnostic_elapsed_time"))
        scores_llm.append(response_data[1].get("LLM_similarity_score"))
        scores_st.append(response_data[2].get("ST_similarity_score"))

    print_stats(["Diagnostic_elapsed_time (s)",
                 "LLM_similarity_score",
                 "ST_similarity_score"],
                [elapsed_time, scores_llm, scores_st])

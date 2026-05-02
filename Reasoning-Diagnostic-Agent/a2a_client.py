from pathlib import Path
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
import sys
import time

import response_agent

from tool_trace import ToolTrace

def extract_json_object(s: str) -> str:
    """Extract and repair the outermost JSON object from a string.

    Returns the extracted JSON object text if found or repaired; otherwise returns
    the original stripped string to let the caller handle parsing failures.
    """
    raw = s.strip()
    first = raw.find('{')
    last = raw.rfind('}')
    if first != -1 and last != -1 and first < last:
        json_text = raw[first:last+1]
        if json_text != raw:
            print("⚠️ Trimmed non-JSON text from LLM_similarity_result")
        return json_text
    elif first != -1 and last == -1:
        json_text = raw[first:] + '}'
        print("⚠️ Appended missing '}' to LLM_similarity_result")
        return json_text
    elif first == -1 and last != -1:
        json_text = '{' + raw[:last+1]
        print("⚠️ Prepended missing '{' to LLM_similarity_result")
        return json_text
    else:
        return raw

async def execute_a2a_agent(agent_card_url: str,
                            user: str,
                            prompt: str | list[str | dict],
                            model: str | None = None,
                            temperature: float | None = None,
                            log_level=ToolTrace.NORMAL) -> tuple[str, int]:

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

        input_dict = {"user": user, "prompt": prompt, "model": model, "temperature": temperature, "log_level": log_level}

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

        if not isinstance(response, Message):
            raise RuntimeError("Response is not a message")

        # Get metadata
        total_tokens = 0
        if isinstance(response.metadata, dict):
            input_tokens = int(response.metadata.get("input_tokens", "0"))
            output_tokens = int(response.metadata.get("output_tokens", "0"))
            total_tokens = input_tokens + output_tokens

        # Extract text from the response Message object
        if not response.parts or len(response.parts) == 0:
            raise RuntimeError("Response message has no parts")

        # Get the first part and extract text from TextPart
        first_part = response.parts[0]
        if isinstance(first_part.root, TextPart):
            if hasattr(first_part.root, 'text') and first_part.root.text is not None:
                return first_part.root.text, total_tokens
            else:
                raise RuntimeError("Part does not have a text attribute")
        else:
            raise RuntimeError(f"Unexpected part type: {type(first_part)}")


class DiagnosticAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class DiagnosticAgent:

    def __init__(self, model: str|None, temperature: float|None, reference_response: str) -> None:
        self.model = model
        self.temperature = temperature
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
        response, total_tokens = asyncio.run(execute_a2a_agent(
            agent_card_url="http://localhost:9001/",
            user="",
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            log_level=ToolTrace.VERBOSE
        ))
        end_time = time.time()
        elapsed_time = f"{(end_time - start_time):.2f}"
        print(f"Elapsed time for execute_a2a_agent: {elapsed_time} seconds")

        return {"messages": [AIMessage(content=[{"Diagnostic_elapsed_time":elapsed_time, "Total_tokens":total_tokens}, response])]}

    def response_agent_node(self, state: DiagnosticAgentState):
        messages = state["messages"]

        # Get diagnostic elapsed time and AI contents
        diagnostic_elapsed_time = ""
        total_tokens = ""
        ai_contents = ""
        if messages and isinstance(messages[1], AIMessage):
            content = messages[1].content
            if isinstance(content, list):
                if len(content) > 0 and isinstance(content[0], dict):
                    diagnostic_elapsed_time = content[0].get("Diagnostic_elapsed_time", "")
                    total_tokens = content[0].get("Total_tokens", "")
                if len(content) > 1 and isinstance(content[1], str):
                    ai_contents = content[1]

        # Get similarity score between response and reference and retry if needed
        MAX_RETRIES = 3
        attempt = 1
        LLM_similarity_result = ""
        LLM_similarity_score: int = 0
        last_parse_error: str | None = None

        while attempt <= MAX_RETRIES:
            LLM_similarity_result = asyncio.run(response_agent.compare_agent_LLM(ai_contents, self.reference_response, self.model))
            print(f"🤖 Response agent node LLM similarity result: {LLM_similarity_result}")

            # Normalize and extract the JSON object
            json_text = extract_json_object(LLM_similarity_result)

            try:
                data = json.loads(json_text)
                parsed_score = data.get("score")
                if isinstance(parsed_score, int):
                    LLM_similarity_score = parsed_score
                    break
                else:
                    last_parse_error = f"Error: LLM score is not an integer: {parsed_score} (type={type(parsed_score)})"
                    print(f"Attempt {attempt}: {last_parse_error}")
            except json.JSONDecodeError as e:
                last_parse_error = f"JSON decode error: {e}"
                print(f"Attempt {attempt}: Failed to parse LLM_similarity_result JSON: {e}")
            except Exception as e:
                last_parse_error = f"Exception during LLM evaluation: {e}"
                print(f"Attempt {attempt}: Exception calling LLM evaluator: {e}")

            attempt += 1

        if LLM_similarity_score == 0 and last_parse_error:
            print(f"Failed to obtain integer LLM score after {MAX_RETRIES} attempts: {last_parse_error}")

        ST_similarity_score = asyncio.run(response_agent.compare_agent_ST(ai_contents, self.reference_response))
        print(f"🤖 Response agent node ST similarity score: {ST_similarity_score}")

        return {"messages": [AIMessage(content=[{
            "Diagnostic_elapsed_time":diagnostic_elapsed_time,
            "LLM_similarity_result":LLM_similarity_result,
            "LLM_similarity_score":LLM_similarity_score,
            "ST_similarity_score":ST_similarity_score,
            "Total_tokens":total_tokens}])]}


def run_diagnostic_and_save(
        iterations: int,
        diag_prompt: str,
        model: str,
        temperature: float,
        save_output_file: str):
    results = []
    start_time = time.time()
    for i in range(1, iterations+1):
        print("----------------------------------------")
        iter_start = time.time()
        response_text, total_tokens_count = asyncio.run(execute_a2a_agent(
            agent_card_url="http://localhost:9001/",
            user="",
            prompt=diag_prompt,
            model=model,
            temperature=temperature,
            log_level=ToolTrace.VERBOSE
        ))
        iter_elapsed = time.time() - iter_start

        print(f"\nAGENT #{i}: [{{'Diagnostic_elapsed_time': '{round(iter_elapsed, 2)}'}}, {{'Total_tokens': {total_tokens_count}}}]")
        print(f"{response_text}")
        results.append({
            "iteration": i,
            "prompt": diag_prompt,
            "response": response_text,
            "total_tokens": total_tokens_count,
            "elapsed_time_seconds": round(iter_elapsed, 2),
            "model": model,
            "temperature": temperature,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        })

    output_path = Path(save_output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    end_time = time.time()
    total_elapsed_time = (end_time - start_time)/60

    print("----------------------------------------")
    print(f"\nSaved {len(results)} iteration results to {output_path}")
    if model:
        print(f"Model: {model}")
    if temperature:
        print(f"Temperature: {temperature}")
    print(f"\nTotal elapsed time: {total_elapsed_time:.1f} minutes\n")


def load_results_from_file(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Saved results file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Saved results file must contain a JSON array of iteration result objects.")
    return data

def evaluate_saved_results(path: Path, diag_agent: DiagnosticAgent) -> tuple[list[dict], float, str, str]:
    saved_results = load_results_from_file(path)
    evaluation_results: list[dict] = []
    model = ""
    temperature = "0.0"
    eval_start = time.time()

    for entry in saved_results:
        iteration = entry.get("iteration")
        response_text = entry.get("response", "")
        elapsed_time_seconds = entry.get("elapsed_time_seconds")
        total_tokens = entry.get("total_tokens")
        if not model:
            model = str(entry.get("model"))
            temperature = str(entry.get("temperature"))

        print("----------------------------------------")
        print(f"Evaluating saved response for iteration #{iteration}")

        state: DiagnosticAgentState = {"messages": [
                HumanMessage("Saved result evaluation"),
                AIMessage(content=[{}, response_text])]}
        evaluated_state = diag_agent.response_agent_node(state)

        evaluated_content = evaluated_state["messages"][-1].content
        if (isinstance(evaluated_content, list) and
            isinstance(evaluated_content[0], dict)):
            llm_result = evaluated_content[0].get("LLM_similarity_result", 0)
            llm_score = evaluated_content[0].get("LLM_similarity_score", 0)
            st_score = evaluated_content[0].get("ST_similarity_score", 0)
        else:
            llm_result = ""
            llm_score = 0
            st_score = 0

        evaluation_results.append({
            "iteration": iteration,
            "prompt": entry.get("prompt"),
            "response": response_text,
            "elapsed_time_seconds": elapsed_time_seconds,
            "total_tokens": total_tokens,
            "LLM_result": llm_result,
            "LLM_similarity_score": int(llm_score) if isinstance(llm_score, int) else 0,
            "ST_similarity_score": int(st_score) if isinstance(st_score, int) else 0,
        })

    eval_end = time.time()
    return evaluation_results, eval_end - eval_start, model, temperature

def run_saved_results_eval(
        input_file: str,
        evaluate_output_file: str,
        reference_response: str):
    diag_agent = DiagnosticAgent(None, None, reference_response)
    input_path = Path(input_file)
    evaluation_results, eval_elapsed, model, temperature = evaluate_saved_results(input_path, diag_agent)

    output_path = Path(evaluate_output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evaluation_results, indent=2, ensure_ascii=False), encoding="utf-8")

    elapsed_time = [entry.get("elapsed_time_seconds", 0) for entry in evaluation_results]
    scores_llm = [entry.get("LLM_similarity_score", 0) for entry in evaluation_results]
    scores_st = [entry.get("ST_similarity_score", 0) for entry in evaluation_results]
    total_tokens = [entry.get("total_tokens", 0) or 0 for entry in evaluation_results]

    print("----------------------------------------")
    print(f"\nEvaluated {len(evaluation_results)} saved responses from {input_path}")
    print(f"Saved evaluation results to {output_path}")
    if model:
        print(f"Model: {model}")
    if temperature:
        print(f"Temperature: {temperature}")
    print_stats(["Diagnostic_elapsed_time (s)",
                    "LLM_similarity_score",
                    "ST_similarity_score",
                    "Total_tokens"],
                [elapsed_time, scores_llm, scores_st, total_tokens])
    print(f"\nTotal diagnostic time: {sum(elapsed_time)/60:.1f} minutes")
    print(f"Total evaluation time: {eval_elapsed/60:.1f} minutes\n")


if __name__ == '__main__':

    from stats import print_stats

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", default="1")
    parser.add_argument("--model", default=None)
    parser.add_argument("--temperature", default=None)

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--save-results", action="store_true",
                            help="Save iteration results to a file instead of running the diagnostic graph")
    mode_group.add_argument("--evaluate-results", action="store_true",
                            help="Read a saved results file and run response evaluation on each saved response")

    parser.add_argument("--input-file", default="a2a_client_results.json",
                        help="Path to the saved results file to evaluate when --evaluate-results is enabled")
    parser.add_argument("--output-file", default=None,
                        help="Path to save results when --save-results or --evaluate-results is enabled")

    args = parser.parse_args()

    reference_response = """
        * The origin service deployment has 2 role instances.
        * The origin service deployment is receiving ≈500 requests/s.
        * Each role instance is receiving ≈250 requests/s.
        * The threshold for normal operation of the origin service is 100 requests/s per role instance.
        * The origin service is over-loaded with too many requests
    """

    diag_prompt = "What is the cause of alert 'Origin service d3f1a8b2-7c4e-4f9e-9e2a-8b6c3a2d1f4e with high latency on more than 90% of requests in the last hour'"
    user_message: DiagnosticAgentState = {"messages": [HumanMessage(diag_prompt)]}

    save_output_file = args.output_file or "a2a_client_results.json"
    evaluate_output_file = args.output_file or "a2a_client_results_evaluation.json"

    if args.save_results:
        run_diagnostic_and_save(int(args.iterations), diag_prompt, args.model, args.temperature, save_output_file)
        sys.exit(0)

    if args.evaluate_results:
        run_saved_results_eval(args.input_file, evaluate_output_file, reference_response)
        sys.exit(0)

    diag_agent = DiagnosticAgent(args.model, args.temperature, reference_response)

    elapsed_time = []
    scores_llm = []
    scores_st = []
    total_tokens = []

    start_time = time.time()
    iterations = int(args.iterations)
    for i in range(1, iterations+1):
        print("----------------------------------------")
        ai_response = diag_agent.diag_graph.invoke(user_message)

        print(f"\nAGENT #{i}: {ai_response['messages'][-1].content}")

        response_data = ai_response["messages"][-1].content
        elapsed_time.append(float(response_data[0].get("Diagnostic_elapsed_time")))
        scores_llm.append(response_data[0].get("LLM_similarity_score"))
        scores_st.append(response_data[0].get("ST_similarity_score"))
        total_tokens.append(int(response_data[0].get("Total_tokens")))

    end_time = time.time()
    total_elapsed_time = (end_time - start_time)/60

    print("\n----------------------------------------")
    if args.model:
        print(f"Model: {args.model}")
    if args.temperature:
        print(f"Temperature: {args.temperature}")

    print_stats(["Diagnostic_elapsed_time (s)",
                 "LLM_similarity_score",
                 "ST_similarity_score",
                 "Total_tokens"],
                [elapsed_time, scores_llm, scores_st, total_tokens])

    print(f"\nTotal elapsed time: {total_elapsed_time:.1f} minutes\n")

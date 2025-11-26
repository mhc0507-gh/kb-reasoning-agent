import json
from langchain.callbacks.base import BaseCallbackHandler


def parse_tool_output(s: str) -> list[str] | str:
    try:
        parsed = json.loads(s)
        return parsed
    except json.JSONDecodeError:
        return s


class ToolTrace(BaseCallbackHandler):
    NORMAL = 0
    VERBOSE = 1
    TRACE = 2
    DEBUG = 3

    logLevel: int

    def __init__(self, level=None):
        ToolTrace.logLevel = level if level is not None else ToolTrace.NORMAL

    @staticmethod
    def printVerbose(traceMsg: str):
        if ToolTrace.logLevel >= ToolTrace.VERBOSE:
            print(traceMsg)

    @staticmethod
    def printTrace(traceMsg: str):
        if ToolTrace.logLevel >= ToolTrace.TRACE:
            print(traceMsg)

    def on_llm_start(self, serialized, prompts, run_id, *args, **kwargs):
        self.printVerbose(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.printVerbose("LLM started:")
        # print(serialized)
        for prompt in prompts:
            self.printVerbose(prompt)
        # print(args)
        # print(kwargs)

    def on_llm_end(self, response, **kwargs):
        self.printVerbose("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.printVerbose("LLM ended:")
        # print(response)
        # print(kwargs)
        for completion in response.generations:
            for generation in completion:
                if "reasoning_content" in generation.message.additional_kwargs:
                    self.printVerbose(f'🤖 {generation.message.additional_kwargs["reasoning_content"]}\n')
                for tool in generation.message.tool_calls:
                    self.printVerbose(f"Need tool call: {tool["name"]} {tool["args"]}")
                self.printTrace(f"Usage: {generation.message.usage_metadata}")
                if generation.text:
                    self.printVerbose("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                    self.printVerbose(f"🤖 {generation.text}")
                    self.printVerbose("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def on_tool_start(self, serialized, input_str, *args, **kwargs):
        self.printVerbose("=======================================")
        self.printVerbose(f"""Tool started: {serialized["name"]} ({serialized["description"]})""")
        self.printVerbose(f"Tool input: {input_str}")

    def on_tool_end(self, output, **kwargs):
        self.printVerbose("---------------------------------------")
        self.printVerbose("Tool finished:")
        parsed = parse_tool_output(output.content)
        if isinstance(parsed, list):
            for idx, item in enumerate(parsed):
                self.printVerbose(f"#{idx}")
                self.printVerbose(item.lstrip())
        else:
            self.printVerbose(output.content)

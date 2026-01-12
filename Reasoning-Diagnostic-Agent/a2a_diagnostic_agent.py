from typing_extensions import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill


import json

import diagnostic_agent

class DiagnosticAgentExecutor(AgentExecutor):
    "Executes functions of the diagnostic agent."

    def __init__(self):
        print("DiagnosticAgentExecutor initialized")

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,) -> None:

        user_input = json.loads(context.get_user_input())
        print("model: ", user_input.get("model"))
        print("prompt received: ", user_input.get("prompt"))
        # Call the diagnostic agent function
        result = await diagnostic_agent.query_agent(
                        prompt=user_input.get("prompt"),
                        model=user_input.get("model"),
                        log_level=user_input.get("log_level"))

        print("Result received: ", result)
        await event_queue.enqueue_event(new_agent_text_message(result))

    @override
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,) -> None:

        raise Exception("Not implemented")

if __name__ == "__main__":

    diagnostic_skill = AgentSkill(
        id="DiagnosticSkill",
        name="Diagnostic Agent Skills",
        description="Performs root cause analysis",
        tags=["diagnostics", "root-cause"],
        examples=[
            "What is the root cause of alert X?",
            "What is the root cause of alert Y?",
            "What is the root cause of alert Z?",
        ],
    )

    diagnostic_agent_card = AgentCard(
        name="Diagnostic Agent",
        description="Performs root cause analysis",
        url="http://localhost:9001/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[diagnostic_skill],
    )

    diagnostic_request_handler = DefaultRequestHandler(
        agent_executor=DiagnosticAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    diagnostic_server = A2AStarletteApplication(
        agent_card=diagnostic_agent_card,
        http_handler=diagnostic_request_handler,
    )

    # Start the Server
    import uvicorn
    uvicorn.run(diagnostic_server.build(),
                host="0.0.0.0",
                port=9001,
                log_level="info")
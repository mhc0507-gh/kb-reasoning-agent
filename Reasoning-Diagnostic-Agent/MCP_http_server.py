import random
import uuid

from dataclasses import dataclass
from fastmcp import FastMCP
from uuid import UUID

mcp_http_server = FastMCP("MCP-HTTP-Server")

# -------------------------------
# Return types
# -------------------------------

@dataclass
class RequestLatencies:
    storage_latency_ms: int
    server_latency_ms: int
    end_to_end_latency_ms: int

@dataclass
class ServiceInfo:
    service_type: str
    account_id: UUID
    deployment_id: UUID

@dataclass
class DeploymentInfo:
    vm_type: str
    role_instances_count: int
    subscription_id: UUID

# -------------------------------
# Tools
# -------------------------------

@mcp_http_server.tool()
def query_system_load(query: str) -> dict:
    """Provides current system load"""

    return { "sytem_load_percent": 99 }

@mcp_http_server.tool()
def query_system_latency(query: str) -> dict:
    """Provides current system latency"""

    return { "system_latency_ms": 100 }

@mcp_http_server.tool()
def query_link_status(query: str) -> dict:
    """Reports whether the link status is connected or disconnected"""

    response = { "link_status": "disconnected" }
    if random.randint(1, 100) < 50:
        response = { "link_status": "connected" }
    return response

@mcp_http_server.tool()
def query_high_latency_request_percentage(service_id: str, time_window: int) -> dict:
    """Reports the percentage of high latency requests on {service-id} in the last {time_window} hours"""

    return { "high_latency_requests_percent": 98 }

@mcp_http_server.tool()
def query_average_request_latencies(service_id: str, time_window: int) -> RequestLatencies:
    """Reports average request latencies on {service-id} in the last {time_window} hours """
    return RequestLatencies(
        storage_latency_ms=10,
        server_latency_ms=500,
        end_to_end_latency_ms=2000)

@mcp_http_server.tool()
def query_service_info(service_id: str) -> ServiceInfo:
    """Reports information on {service-id} """
    return ServiceInfo(
        service_type="shared origin",
        account_id=uuid.UUID("a1d4c6f7-3e2b-4b9a-bc8f-9f6e2a1d7c3e"),
        deployment_id=uuid.UUID("f3c9a7e2-8b4d-4f6a-9c2e-7d1b3a6e5c9f"))

@mcp_http_server.tool()
def query_deployment_info(deployment_id: str) -> DeploymentInfo:
    """Reports information on {deployment_id}"""
    return DeploymentInfo(
        vm_type="Standard_D16_v5",
        role_instances_count=2,
        subscription_id=uuid.UUID("c7e2b9f1-4d3a-4a8e-9f6c-2b1d7e3f9a4c"))

@mcp_http_server.tool()
def query_average_cpu_load(deployment_id: str, time_window: int) -> dict:
    """Reports the average CPU load on {deployment-id} in the last {time_window} hours"""

    return { "average_cpu_load_percent": 98 }

@mcp_http_server.tool()
def query_average_requests_per_sec(deployment_id: str, time_window: int) -> dict:
    """Reports the average requests per second on {deployment-id} in the last {time_window} hours"""

    return { "average_requests_per_second": 500 }


# -------------------------------
# Prompt
# -------------------------------

@mcp_http_server.prompt()
def get_llm_prompt(query: str) -> str:
    """Generates a prompt for the LLM to use to answer the query"""

    raise Exception("Not implemented")


if __name__ == "__main__":
    mcp_http_server.run(transport="streamable-http",
                        host="localhost",
                        port=8000,
                        path="/mcp",
                        log_level="debug")
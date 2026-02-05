from prometheus_client import Counter, Histogram, start_http_server
import time

# --- Metric Definitions (Must match Grafana Queries) ---

# Histogram: maos_agent_task_duration_seconds
TASK_DURATION = Histogram(
    'maos_agent_task_duration_seconds',
    'Time spent executing the agent task',
    ['task_type', 'service_name', 'version']
)

# Counter: maos_agent_tool_calls_total
TOOL_CALLS = Counter(
    'maos_agent_tool_calls_total',
    'Total number of tool invocations',
    ['tool_name', 'status', 'service_name', 'version']
)

# Counter: maos_agent_token_usage_total
TOKEN_USAGE = Counter(
    'maos_agent_token_usage_total',
    'Total LLM tokens consumed',
    ['model', 'type', 'service_name', 'version']
)

# Histogram: maos_agent_steps_per_goal
STEPS_PER_GOAL = Histogram(
    'maos_agent_steps_per_goal',
    'Number of cognitive steps taken to solve a goal',
    ['task_type', 'service_name', 'version'],
    buckets=[1, 3, 5, 10, 20, 50] # Optimized for "Loop of Death" detection
)

# Counter: maos_agent_task_success_total
TASK_SUCCESS = Counter(
    'maos_agent_task_success_total',
    'Total task completions',
    ['task_type', 'status', 'service_name', 'version']
)

class MetricsManager:
    def __init__(self, service_name: str, version: str = "v1", port: int = 8000):
        self.labels = {"service_name": service_name, "version": version}
        # Start the Prometheus exporter server automatically
        try:
            start_http_server(port)
            print(f"[Maos] Metrics server started on port {port}")
        except Exception as e:
            print(f"[Maos] Warning: Could not start metrics server: {e}")

    def record_tool(self, tool_name: str, status: str = "success"):
        TOOL_CALLS.labels(tool_name=tool_name, status=status, **self.labels).inc()

    def record_tokens(self, count: int, model: str = "unknown", type: str = "total"):
        TOKEN_USAGE.labels(model=model, type=type, **self.labels).inc(count)

    def record_task_success(self, task_type: str, status: str):
        TASK_SUCCESS.labels(task_type=task_type, status=status, **self.labels).inc()

    def task_timer(self, task_type: str):
        """Returns a context manager to time a task."""
        return TASK_DURATION.labels(task_type=task_type, **self.labels).time()
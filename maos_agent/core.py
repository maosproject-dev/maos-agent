from .metrics import MetricsManager
from .lifecycle import LifecycleManager
from .decorators import TaskContext, instrument_tool

class MaosAgent:
    def __init__(self, service_name: str, version: str = "v1.0", metrics_port: int = 8000):
        self.service_name = service_name
        self.metrics = MetricsManager(service_name, version, metrics_port)
        self.lifecycle = LifecycleManager()

    def check_health(self):
        """
        Proxy to lifecycle check. 
        Raises SpotInterruptionError if the node is dying.
        """
        self.lifecycle.check_health()

    def tool(self, name: str = None):
        """
        Decorator to track tool usage automatically.
        Usage: @agent.tool(name="search")
        """
        return instrument_tool(self.metrics, name)

    def task(self, name: str):
        """
        Context manager for the main job loop.
        Usage: with agent.task("analyze") as task: ...
        """
        return TaskContext(self.metrics, name)
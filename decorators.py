import functools
import time
import logging

# We import metrics inside the methods to avoid circular imports 
# or we pass the metrics manager object into these classes.

class TaskContext:
    """
    Context manager for a unit of work (Task).
    Tracks duration, step count, and final success/failure status.
    """
    def __init__(self, metrics, name: str):
        self.metrics = metrics
        self.name = name
        self.start_time = time.time()
        self.steps = 0
        self.logger = logging.getLogger("maos.agent")

    def __enter__(self):
        self.logger.info(f"Starting task: {self.name}")
        return self

    def step(self):
        """
        Record a 'cognitive step' (e.g., one LLM thought loop).
        """
        self.steps += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "error" if exc_type else "success"
        
        # 1. Record Success/Fail Counter
        self.metrics.record_task_success(self.name, status)
        
        # 2. Record Duration
        # We manually observe the histogram since we managed the time
        from .metrics import TASK_DURATION
        TASK_DURATION.labels(
            task_type=self.name, 
            **self.metrics.labels
        ).observe(duration)

        # 3. Record Steps (The "Loop of Death" check)
        from .metrics import STEPS_PER_GOAL
        STEPS_PER_GOAL.labels(
            task_type=self.name, 
            **self.metrics.labels
        ).observe(self.steps)

        if exc_type:
            self.logger.error(f"Task '{self.name}' failed: {exc_val}")


def instrument_tool(metrics, name: str = None):
    """
    Factory that returns the actual decorator.
    We pass 'metrics' (the manager instance) in so the decorator knows where to record.
    """
    def decorator(func):
        # Use the provided name or default to the function name
        tool_name = name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Record Success
                metrics.record_tool(tool_name, status="success")
                return result
            except Exception as e:
                # Record Failure & Re-raise
                metrics.record_tool(tool_name, status="error")
                raise e
        return wrapper
    return decorator